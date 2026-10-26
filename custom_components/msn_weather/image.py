"""Weather map image entities (the maps of msn.com/weather/maps)."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.image import ImageEntity
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import (
    CONF_IMAGE_SECRET,
    CONF_MAP_FRAME_MS,
    CONF_MAP_FRAMES,
    CONF_MAP_HIRES,
    CONF_MAP_HEIGHT,
    CONF_MAP_WIDTH,
    DEFAULT_MAP_FRAME_MS,
    DEFAULT_MAP_FRAMES,
    DEFAULT_MAP_HEIGHT,
    DEFAULT_MAP_WIDTH,
)
from .coordinator import MsnWeatherConfigEntry, MsnWeatherCoordinator
from .entity import MsnWeatherEntity
from .maps import ANIMATION, LAYERS, MsnMapRenderer, encode_animation, storm_frame_times

_LOGGER = logging.getLogger(__name__)

ENABLED_BY_DEFAULT = {
    "temperature", "precipitation", "wind", "clouds", "satellite", "alerts",
    "lightning", "tropical_cyclones", "radar",
}

TITLES = {
    "de": {
        "temperature": "Temperatur",
        "precipitation": "Niederschlag",
        "wind": "Wind",
        "clouds": "Wolken",
        "humidity": "Luftfeuchtigkeit",
        "visibility": "Sichtweite",
        "pressure": "Luftdruck",
        "dew_point": "Taupunkt",
        "air_quality": "Luftqualität",
        "pollen": "Pollen",
        "satellite": "Satellit",
        "alerts": "Unwetter",
        "winter": "Winterwetter",
        "lightning": "Blitze",
        "tropical_cyclones": "Tropischer Zyklon",
        "radar": "Regenradar",
    },
    "it": {
        "temperature": "Temperatura",
        "precipitation": "Precipitazioni",
        "wind": "Vento",
        "clouds": "Nuvole",
        "humidity": "Umidità",
        "visibility": "Visibilità",
        "pressure": "Pressione",
        "dew_point": "Punto di rugiada",
        "air_quality": "Qualità dell'aria",
        "pollen": "Pollini",
        "satellite": "Satellite",
        "alerts": "Allerte meteo",
        "winter": "Meteo invernale",
        "lightning": "Fulmini",
        "tropical_cyclones": "Ciclone tropicale",
        "radar": "Radar precipitazioni",
    },
    "fr": {
        "temperature": "Température", "precipitation": "Précipitations", "wind": "Vent", "clouds": "Nuages",
        "humidity": "Humidité", "visibility": "Visibilité", "pressure": "Pression", "dew_point": "Point de rosée",
        "air_quality": "Qualité de l'air", "pollen": "Pollen", "satellite": "Satellite", "alerts": "Intempéries",
        "winter": "Météo hivernale", "lightning": "Foudre", "tropical_cyclones": "Cyclone tropical",
        "radar": "Radar des précipitations",
    },
    "es": {
        "temperature": "Temperatura", "precipitation": "Precipitación", "wind": "Viento", "clouds": "Nubes",
        "humidity": "Humedad", "visibility": "Visibilidad", "pressure": "Presión", "dew_point": "Punto de rocío",
        "air_quality": "Calidad del aire", "pollen": "Polen", "satellite": "Satélite", "alerts": "Tiempo severo",
        "winter": "Tiempo invernal", "lightning": "Rayos", "tropical_cyclones": "Ciclón tropical",
        "radar": "Radar de precipitación",
    },
    "nl": {
        "temperature": "Temperatuur", "precipitation": "Neerslag", "wind": "Wind", "clouds": "Wolken",
        "humidity": "Luchtvochtigheid", "visibility": "Zicht", "pressure": "Luchtdruk", "dew_point": "Dauwpunt",
        "air_quality": "Luchtkwaliteit", "pollen": "Pollen", "satellite": "Satelliet", "alerts": "Noodweer",
        "winter": "Winterweer", "lightning": "Bliksem", "tropical_cyclones": "Tropische cycloon",
        "radar": "Neerslagradar",
    },
    "en": {
        "temperature": "Temperature",
        "precipitation": "Precipitation",
        "wind": "Wind",
        "clouds": "Clouds",
        "humidity": "Humidity",
        "visibility": "Visibility",
        "pressure": "Pressure",
        "dew_point": "Dew point",
        "air_quality": "Air quality",
        "pollen": "Pollen",
        "satellite": "Satellite",
        "alerts": "Severe weather",
        "winter": "Winter weather",
        "lightning": "Lightning",
        "tropical_cyclones": "Tropical cyclone",
        "radar": "Precipitation radar",
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MsnWeatherConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        MsnMapImage(hass, coordinator, coordinator.map_renderer, key) for key in LAYERS
    )
    # fixed zoom per map, e.g. set by the zoom field of the map card (no zoom = the shared map zoom)
    entity_platform.async_get_current_platform().async_register_entity_service(
        "set_map_zoom",
        {vol.Optional("zoom"): vol.Any(None, vol.All(vol.Coerce(int), vol.Range(min=3, max=11)))},
        "async_set_map_zoom",
    )


class MsnMapImage(MsnWeatherEntity, ImageEntity):
    """A rendered weather map centred on the configured location."""

    _platform_domain = "image"
    _attr_content_type = "image/png"
    _unrecorded_attributes = frozenset({"frames", "legend"})

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: MsnWeatherCoordinator,
        renderer: MsnMapRenderer,
        key: str,
    ) -> None:
        MsnWeatherEntity.__init__(self, coordinator, f"map_{key}")
        ImageEntity.__init__(self, hass)
        # Stable access token: survives restarts, so dashboards/apps that are still open
        # keep loading the map instead of producing failed logins (and IP bans).
        secret = coordinator.config_entry.data.get(CONF_IMAGE_SECRET, coordinator.config_entry.entry_id)
        self._stable_token = hmac.new(
            secret.encode(), self._attr_unique_id.encode(), hashlib.sha256
        ).hexdigest()
        self.access_tokens.clear()
        self.access_tokens.append(self._stable_token)
        self._key = key
        self._renderer = renderer
        self._attr_translation_key = f"map_{key}"
        self._attr_entity_registry_enabled_default = key in ENABLED_BY_DEFAULT
        self._attr_image_last_updated = dt_util.utcnow()
        self._image: bytes | None = None
        self._image_key: tuple | None = None
        self._lock = asyncio.Lock()
        self._result_attrs: dict[str, Any] = {}
        self._task: asyncio.Task | None = None
        self._zoom: int | None = None  # fixed zoom of this map (map card setting)
        self._requested = False

    @callback
    def async_update_token(self) -> None:
        """Keep the stable token instead of rotating a random one every few minutes."""
        token = getattr(self, "_stable_token", None)
        if token is None:  # called from ImageEntity.__init__ before our token exists
            super().async_update_token()
            return
        if not self.access_tokens or self.access_tokens[-1] != token:
            self.access_tokens.append(token)

    @callback
    def _handle_coordinator_update(self) -> None:
        # Keep a map that has been viewed up to date in the background, so the
        # frontend never waits for a render (HA's image proxy times out after 10 s).
        if self._requested:
            self._ensure_render()
        super()._handle_coordinator_update()

    async def async_will_remove_from_hass(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
        await super().async_will_remove_from_hass()

    async def async_set_map_zoom(self, zoom: int | None = None) -> None:
        """Give this map its own zoom (None: follow the shared map zoom)."""
        self._zoom = zoom
        self._ensure_render()
        self.async_write_ha_state()

    @callback
    def _ensure_render(self) -> asyncio.Task | None:
        """Start a background render when the map would change (new hour, offset, options)."""
        key = self._render_key()
        if self._image is not None and self._image_key == key:
            return None
        if self._task is None or self._task.done():
            self._task = self.hass.async_create_background_task(
                self._async_render(key), f"msn_weather render {self.entity_id}"
            )
        return self._task

    def _frames(self) -> tuple[int, int, str]:
        options = self.coordinator.config_entry.options
        frames = int(options.get(CONF_MAP_FRAMES, DEFAULT_MAP_FRAMES))
        mode, step = ANIMATION.get(self._key, (None, 0))
        if frames <= 1 or mode is None:
            return 1, 0, ""
        return frames, step, mode

    def _render_key(self) -> tuple:
        options = self.coordinator.config_entry.options
        now = dt_util.utcnow()
        return (
            now.strftime("%Y%m%d%H"),
            now.minute // 10 if self._key == "satellite" else now.minute // 4 if self._key == "radar" else 0,
            self.coordinator.map_offset,
            self._zoom or self.coordinator.map_zoom,
            options.get(CONF_MAP_WIDTH, DEFAULT_MAP_WIDTH),
            options.get(CONF_MAP_HEIGHT, DEFAULT_MAP_HEIGHT),
            self._frames(),
            2 if options.get(CONF_MAP_HIRES, True) else 1,
            self._storm_key(),
            self._frame_ms,
        )

    @property
    def _frame_ms(self) -> int:
        return int(self.coordinator.config_entry.options.get(CONF_MAP_FRAME_MS, DEFAULT_MAP_FRAME_MS))

    def _storm_key(self) -> tuple:
        if self._key != "tropical_cyclones" or not self.coordinator.data:
            return ()
        focus = self.coordinator.focused_storm
        return (
            focus and focus.get("id"),
            focus and focus.get("time"),
            tuple(s.get("id") for s in self.coordinator.data.storms_visible),
        )

    async def async_image(self) -> bytes | None:
        self._requested = True
        task = self._ensure_render()
        if task is not None and self._image is None:
            # First view: wait a bit for the render, but stay below the proxy timeout.
            await asyncio.wait({task}, timeout=8)
        return self._image

    async def _async_render(self, key: tuple) -> None:
        async with self._lock:
            entry = self.coordinator.config_entry
            lang = self.coordinator.language[:2]
            base_title = TITLES.get(lang, TITLES["en"]).get(self._key, self._key)
            offset = self.coordinator.map_offset if LAYERS[self._key].supports_forecast else 0
            count, step, mode = self._frames()
            focus = self.coordinator.focused_storm if self._key == "tropical_cyclones" else None
            nowcast: list[int] = [0] * max(count, 1)
            if mode == "hours":
                plan = [(offset + i * step, 0, None) for i in range(count)]
            elif mode == "nowcast":
                # about a third of the frames look back, the rest ahead (MSN: -2 h … +3 h)
                past = count // 3
                nowcast = [(i - past) * step for i in range(count)]
                plan = [(0, 0, None)] * count
            elif mode == "minutes_back":
                plan = [(0, (count - 1 - i) * step, None) for i in range(count)]
            elif mode == "storm":
                # the storm moves along its observed + forecast track
                plan = [(0, 0, t) for t in storm_frame_times(focus, count)] or [(0, 0, None)]
            else:
                plan = [(offset, 0, None)]
            storms = (
                self.coordinator.data.storms_visible
                if self.coordinator.data and self._key == "tropical_cyclones"
                else []
            )
            results = []
            try:
                for index, (hours, minutes_back, storm_time) in enumerate(plan):
                    title = base_title + (f" +{hours} h" if hours else "")
                    if mode == "nowcast" and nowcast[index]:
                        title = f"{base_title} {nowcast[index]:+d} min"
                    results.append(
                        await self._renderer.render(
                            self._key,
                            entry.data[CONF_LATITUDE],
                            entry.data[CONF_LONGITUDE],
                            zoom=int(key[3]),
                            width=int(key[4]),
                            height=int(key[5]),
                            offset_hours=hours,
                            title=title,
                            tz=dt_util.get_default_time_zone(),
                            storms=storms,
                            shift_minutes=minutes_back,
                            scale=int(key[7]),
                            storm_id=focus.get("id") if focus else None,
                            storm_time=storm_time,
                            nowcast_minutes=nowcast[index],
                        )
                    )
                if len(results) > 1:
                    self._image = await self.hass.async_add_executor_job(
                        encode_animation, [r.image for r in results], self._frame_ms
                    )
                    self._attr_content_type = "image/webp"
                else:
                    self._image = results[0].image
                    self._attr_content_type = "image/png"
            except Exception:  # noqa: BLE001 - never break the frontend
                _LOGGER.exception("Rendering map %s failed", self._key)
                return
            first = results[0]
            if mode == "minutes_back":
                first = results[-1]
            elif mode == "nowcast":
                first = results[min(count // 3, len(results) - 1)]
            self._image_key = key
            self._result_attrs = {
                "valid_time": first.valid_time.isoformat() if first.valid_time else None,
                "value_at_location": round(first.value, 2) if first.value is not None else None,
                "unit": first.unit or None,
                "forecast_hours": offset,
                "supports_forecast": LAYERS[self._key].supports_forecast,
                "frames": [r.valid_time.isoformat() for r in results if r.valid_time],
                "animated": len(results) > 1,
                "width": int(key[4]),
                "height": int(key[5]),
                "pixel_ratio": int(key[7]),
                "zoom": int(key[3]),
                "fixed_zoom": self._zoom,
                # for the map card when the title / legend are not drawn into the image
                "title": base_title,
                "labels_in_image": self._renderer.labels,
                "legend": self._renderer.legend_info(self._key),
                "frame_ms": self._frame_ms,
            }
        self._attr_image_last_updated = dt_util.utcnow()
        if self._render_key() != key:
            # the forecast hour / zoom changed while rendering: render the new map right away
            self.hass.loop.call_soon(self._ensure_render)
        if self.hass and self.enabled:
            self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self._result_attrs
