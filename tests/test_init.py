"""Setting up the integration with recorded data."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er, issue_registry as ir
from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.msn_weather.api import MsnWeatherAuthError
from custom_components.msn_weather.const import (
    CONF_CYCLONE_RADIUS,
    CONF_IMAGE_SECRET,
    CONF_LANGUAGE,
    CONF_USE_HOME,
    DOMAIN,
)

from .conftest import LAT, LON


async def _setup(hass: HomeAssistant, options: dict | None = None) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Upper East Side",
        unique_id="40.774_-73.957_en-us",
        data={
            CONF_NAME: "Upper East Side",
            CONF_LATITUDE: LAT,
            CONF_LONGITUDE: LON,
            CONF_LANGUAGE: "en-us",
            CONF_IMAGE_SECRET: "test-secret",
        },
        options=options or {},
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_setup_and_unload(hass: HomeAssistant, mock_client, mock_frontend) -> None:
    entry = await _setup(hass)
    assert entry.state is ConfigEntryState.LOADED

    weather = hass.states.get("weather.upper_east_side")
    assert weather is not None
    assert weather.attributes["temperature_unit"] == "°C"
    assert weather.attributes["wind_speed_unit"] == "km/h"
    # entity ids are language independent
    for entity_id in (
        "sensor.upper_east_side_umbrella",
        "sensor.upper_east_side_tropical_cyclones",
        "binary_sensor.upper_east_side_alert_active",
        "binary_sensor.upper_east_side_cyclone_nearby",
        "number.upper_east_side_map_forecast_hours",
        "select.upper_east_side_cyclone_map_storm",
        "image.upper_east_side_map_precipitation",
    ):
        assert hass.states.get(entity_id) is not None, entity_id
    assert len(er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)) > 60
    assert mock_client.client_cls.call_args.kwargs["imperial"] is False

    assert await hass.config_entries.async_unload(entry.entry_id)
    assert entry.state is ConfigEntryState.NOT_LOADED


async def test_imperial_units(hass: HomeAssistant, mock_client, mock_frontend) -> None:
    hass.config.units = US_CUSTOMARY_SYSTEM
    await _setup(hass)
    assert mock_client.client_cls.call_args.kwargs["imperial"] is True
    weather = hass.states.get("weather.upper_east_side")
    assert weather.attributes["temperature_unit"] == "°F"
    assert weather.attributes["wind_speed_unit"] == "mph"
    assert weather.attributes["pressure_unit"] == "inHg"


async def test_cyclones_worldwide(hass: HomeAssistant, mock_client, mock_frontend, storms) -> None:
    await _setup(hass)
    assert hass.states.get("sensor.upper_east_side_tropical_cyclones").state == "2"
    assert hass.states.get("binary_sensor.upper_east_side_cyclone_nearby").state == "on"
    select = hass.states.get("select.upper_east_side_cyclone_map_storm")
    assert select.state == "auto"
    assert select.attributes["options"] == ["auto", *sorted(
        (s["name"] for s in storms), key=lambda n: -next(s["max_wind"] for s in storms if s["name"] == n)
    )]

    other = select.attributes["options"][-1]
    await hass.services.async_call(
        "select", "select_option",
        {"entity_id": "select.upper_east_side_cyclone_map_storm", "option": other}, blocking=True,
    )
    assert hass.states.get("select.upper_east_side_cyclone_map_storm").state == other


async def test_cyclone_radius(hass: HomeAssistant, mock_client, mock_frontend) -> None:
    await _setup(hass, {CONF_CYCLONE_RADIUS: 100})
    assert hass.states.get("sensor.upper_east_side_tropical_cyclones").state == "0"
    assert hass.states.get("binary_sensor.upper_east_side_cyclone_nearby").state == "off"
    assert hass.states.get("select.upper_east_side_cyclone_map_storm").attributes["options"] == ["auto"]


async def test_api_key_rotation(hass: HomeAssistant, mock_client, mock_frontend) -> None:
    good = mock_client.async_get.side_effect

    async def get():
        if mock_client.api_key == "old-key":
            raise MsnWeatherAuthError("HTTP 401")
        return good()

    mock_client.async_get.side_effect = get
    with patch(
        "custom_components.msn_weather.coordinator.async_discover_api_key",
        AsyncMock(return_value="new-key"),
    ):
        entry = await _setup(hass)
    assert entry.state is ConfigEntryState.LOADED
    assert mock_client.api_key == "new-key"


async def test_api_key_rejected(hass: HomeAssistant, mock_client, mock_frontend) -> None:
    mock_client.async_get.side_effect = MsnWeatherAuthError("HTTP 401")
    with patch(
        "custom_components.msn_weather.coordinator.async_discover_api_key",
        AsyncMock(return_value=None),
    ):
        entry = await _setup(hass)
    assert entry.state is ConfigEntryState.SETUP_RETRY
    assert ir.async_get(hass).async_get_issue(DOMAIN, f"api_key_{entry.entry_id}") is not None


async def test_follows_home_location(hass: HomeAssistant, mock_client, mock_frontend) -> None:
    """Entries created with "use the Home Assistant location" pick up a moved location."""
    hass.config.latitude, hass.config.longitude = 41.0, -73.0
    entry = MockConfigEntry(
        domain=DOMAIN, title="Home",
        data={CONF_NAME: "Home", CONF_LATITUDE: LAT, CONF_LONGITUDE: LON, CONF_LANGUAGE: "en-us",
              CONF_IMAGE_SECRET: "s", CONF_USE_HOME: True},
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert (entry.data[CONF_LATITUDE], entry.data[CONF_LONGITUDE]) == (41.0, -73.0)
