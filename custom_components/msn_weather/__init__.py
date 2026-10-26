"""The MSN Weather integration."""

from __future__ import annotations

import hashlib
import secrets
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, EVENT_CORE_CONFIG_UPDATE, Platform
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import CONF_IMAGE_SECRET, CONF_USE_HOME, DOMAIN
from .coordinator import MsnWeatherConfigEntry, MsnWeatherCoordinator

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
CARDS_URL = "/msn_weather_static"
CARDS_FILE = Path(__file__).parent / "frontend" / "msn-weather-cards.js"

PLATFORMS = [
    Platform.WEATHER,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.IMAGE,
    Platform.NUMBER,
    Platform.SELECT,
]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Serve and auto-load the bundled Lovelace cards."""
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARDS_URL, str(CARDS_FILE.parent), False)]
    )
    # The loader imports the cards with a time-based cache buster, so card updates
    # reach the browser without restarting Home Assistant.
    digest = await hass.async_add_executor_job(
        lambda: hashlib.sha1(CARDS_FILE.read_bytes()).hexdigest()[:10]
    )
    add_extra_js_url(hass, f"{CARDS_URL}/msn-weather-cards-loader.js?v={digest}")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: MsnWeatherConfigEntry) -> bool:
    if CONF_IMAGE_SECRET not in entry.data:
        # per-entry secret for the stable image access tokens (created once)
        hass.config_entries.async_update_entry(
            entry, data={**entry.data, CONF_IMAGE_SECRET: secrets.token_hex(32)}
        )
    if entry.data.get(CONF_USE_HOME) and (
        entry.data.get(CONF_LATITUDE) != hass.config.latitude
        or entry.data.get(CONF_LONGITUDE) != hass.config.longitude
    ):
        # the Home Assistant location moved: use the new coordinates
        hass.config_entries.async_update_entry(
            entry,
            data={**entry.data, CONF_LATITUDE: hass.config.latitude, CONF_LONGITUDE: hass.config.longitude},
        )
    coordinator = MsnWeatherCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    if entry.data.get(CONF_USE_HOME):

        @callback
        def _core_config_updated(event: Event) -> None:
            if (entry.data.get(CONF_LATITUDE), entry.data.get(CONF_LONGITUDE)) != (
                hass.config.latitude, hass.config.longitude
            ):
                hass.config_entries.async_schedule_reload(entry.entry_id)

        entry.async_on_unload(hass.bus.async_listen(EVENT_CORE_CONFIG_UPDATE, _core_config_updated))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: MsnWeatherConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload(hass: HomeAssistant, entry: MsnWeatherConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
