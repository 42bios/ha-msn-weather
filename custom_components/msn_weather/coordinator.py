"""Data update coordinator for MSN Weather."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util
from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM

from .api import (
    MsnWeatherAuthError,
    MsnWeatherClient,
    MsnWeatherData,
    MsnWeatherError,
    async_discover_api_key,
)
from .maps import MsnMapRenderer
from .units import KM_PER_MILE
from .const import (
    CONF_API_KEY,
    CONF_CYCLONE_DISTURBANCES,
    CONF_CYCLONE_FOCUS,
    CONF_CYCLONE_RADIUS,
    CONF_LANGUAGE,
    CONF_MAP_LABELS,
    CONF_MAP_ZOOM,
    CONF_SCAN_INTERVAL,
    CYCLONE_AUTO,
    DEFAULT_API_KEY,
    DEFAULT_CYCLONE_FOCUS,
    DEFAULT_CYCLONE_RADIUS,
    DEFAULT_LANGUAGE,
    DEFAULT_MAP_ZOOM,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

type MsnWeatherConfigEntry = ConfigEntry[MsnWeatherCoordinator]

STORAGE_KEY = f"{DOMAIN}.api_key"
STORAGE_VERSION = 1


@dataclass
class MsnWeatherShared:
    """State shared by all entries: the API key found on msn.com, kept across restarts."""

    store: Store[dict[str, str]]
    api_key: str | None = None

    async def async_set_api_key(self, key: str) -> None:
        if key != self.api_key:
            self.api_key = key
            await self.store.async_save({"api_key": key})


async def async_load_shared(hass: HomeAssistant) -> MsnWeatherShared:
    """Load the shared state once."""
    if (shared := hass.data.get(DOMAIN)) is None:
        shared = hass.data[DOMAIN] = MsnWeatherShared(Store(hass, STORAGE_VERSION, STORAGE_KEY))
        shared.api_key = (await shared.store.async_load() or {}).get("api_key")
    return shared


def automatic_api_key(hass: HomeAssistant) -> str:
    """Key used when the options hold none: the one found on msn.com, else the built-in one."""
    shared: MsnWeatherShared | None = hass.data.get(DOMAIN)
    return (shared.api_key if shared else None) or DEFAULT_API_KEY


class MsnWeatherCoordinator(DataUpdateCoordinator[MsnWeatherData]):
    """Fetch data from MSN periodically."""

    config_entry: MsnWeatherConfigEntry

    def __init__(self, hass: HomeAssistant, entry: MsnWeatherConfigEntry) -> None:
        options = entry.options
        # options override the language chosen during setup
        self.language: str = options.get(CONF_LANGUAGE) or entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
        # values follow the Home Assistant unit system (US customary -> °F, mph, inHg, mi, in)
        self.imperial: bool = hass.config.units is US_CUSTOMARY_SYSTEM
        api_key = options.get(CONF_API_KEY) or automatic_api_key(hass)
        self.client = MsnWeatherClient(
            async_get_clientsession(hass),
            entry.data[CONF_LATITUDE],
            entry.data[CONF_LONGITUDE],
            self.language,
            api_key,
            imperial=self.imperial,
        )
        self.map_renderer = MsnMapRenderer(
            async_get_clientsession(hass),
            api_key,
            self.language,
            imperial=self.imperial,
        )
        self.map_renderer.labels = bool(options.get(CONF_MAP_LABELS, True))
        self.map_offset = 0
        # live map zoom (number entity), starts at the zoom from the options
        self.map_zoom: int = int(options.get(CONF_MAP_ZOOM, DEFAULT_MAP_ZOOM))
        # storm shown on the tropical cyclone map: CYCLONE_AUTO or a storm name
        self.cyclone_selection: str = CYCLONE_AUTO
        self._storms: list = []
        self._storms_fetched = None
        self._climate: dict = {}
        self._monthly: list = []
        self._climate_fetched = None
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(
                minutes=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            ),
        )

    async def _async_update_data(self) -> MsnWeatherData:
        try:
            try:
                data = await self.client.async_get()
            except MsnWeatherAuthError:
                await self._async_refresh_api_key()
                data = await self.client.async_get()
                # the new key works: keep it for the next start and for other entries
                if (shared := self.hass.data.get(DOMAIN)) is not None:
                    await shared.async_set_api_key(self.client.api_key)
        except MsnWeatherAuthError as err:
            ir.async_create_issue(
                self.hass, DOMAIN, f"api_key_{self.config_entry.entry_id}",
                is_fixable=True, severity=ir.IssueSeverity.ERROR,
                translation_key="api_key_invalid",
                data={"entry_id": self.config_entry.entry_id},
                translation_placeholders={"name": self.config_entry.title},
            )
            raise UpdateFailed("MSN rejected the API key and no new key could be found") from err
        except MsnWeatherError as err:
            raise UpdateFailed(f"Error fetching MSN weather data: {err}") from err
        ir.async_delete_issue(self.hass, DOMAIN, f"api_key_{self.config_entry.entry_id}")
        data.fetched = dt_util.utcnow()
        data.imperial = self.imperial
        if self._storms_fetched is None or data.fetched - self._storms_fetched > timedelta(
            minutes=30
        ):
            try:
                self._storms = await self.client.async_get_storms()
                self._storms_fetched = data.fetched
            except MsnWeatherError as err:
                _LOGGER.debug("Tropical cyclone data unavailable: %s", err)
        data.storms = self._storms
        data.storms_visible = self._filter_storms(self._storms)
        if self._climate_fetched is None or data.fetched - self._climate_fetched > timedelta(hours=6):
            try:
                self._climate, self._monthly = await self.client.async_get_climate()
                self._climate_fetched = data.fetched
            except MsnWeatherError as err:
                _LOGGER.debug("Climate data unavailable: %s", err)
        data.climate = self._climate
        data.monthly = self._monthly
        return data

    async def _async_refresh_api_key(self) -> None:
        """MSN rotated its public key: read the current one from msn.com."""
        key = await async_discover_api_key(async_get_clientsession(self.hass))
        if not key or key == self.client.api_key:
            raise MsnWeatherAuthError("no new API key found")
        _LOGGER.info("MSN API key was rotated, using the key from msn.com")
        self.client.api_key = key
        self.map_renderer.set_api_key(key)

    def _filter_storms(self, storms: list[dict]) -> list[dict]:
        """Apply radius / disturbance options and order by map priority."""
        options = self.config_entry.options
        radius = float(options.get(CONF_CYCLONE_RADIUS, DEFAULT_CYCLONE_RADIUS) or 0)
        if self.imperial:  # entered in miles
            radius *= KM_PER_MILE
        with_disturbances = options.get(CONF_CYCLONE_DISTURBANCES, True)
        out = [
            s for s in storms
            if s.get("latitude") is not None
            and (with_disturbances or not s["disturbance"])
            and (not radius or (s.get("closest_km") is not None and s["closest_km"] <= radius))
        ]
        if options.get(CONF_CYCLONE_FOCUS, DEFAULT_CYCLONE_FOCUS) == "nearest":
            out.sort(key=lambda s: (s["disturbance"], s.get("distance_km") or 1e9))
        else:
            out.sort(key=lambda s: (s["disturbance"], -(s.get("max_wind") or 0), s.get("distance_km") or 1e9))
        return out

    @property
    def focused_storm(self) -> dict | None:
        """Storm the tropical cyclone map is centred on."""
        storms = self.data.storms_visible if self.data else []
        chosen = next((s for s in storms if s.get("name") == self.cyclone_selection), None)
        return chosen or next((s for s in storms if not s["disturbance"]), None)
