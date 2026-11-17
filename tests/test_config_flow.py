"""Config and options flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.msn_weather.api import MsnWeatherError, parse_response
from custom_components.msn_weather.const import (
    CONF_API_KEY,
    CONF_CYCLONE_FOCUS,
    CONF_CYCLONE_RADIUS,
    CONF_LANGUAGE,
    CONF_MSN_URL,
    CONF_USE_HOME,
    DEFAULT_API_KEY,
    DOMAIN,
)

from .conftest import LAT, LON, load

USER_INPUT = {
    CONF_NAME: "Upper East Side",
    CONF_LOCATION: {CONF_LATITUDE: LAT, CONF_LONGITUDE: LON},
    CONF_LANGUAGE: "en-us",
}


@pytest.fixture
def flow_client():
    with (
        patch("custom_components.msn_weather.config_flow.MsnWeatherClient") as cls,
        patch("custom_components.msn_weather.async_setup_entry", AsyncMock(return_value=True)),
        patch("custom_components.msn_weather.async_setup", AsyncMock(return_value=True)),
    ):
        cls.return_value.async_get = AsyncMock(return_value=parse_response(load("overview.json")))
        yield cls.return_value


async def test_user_flow(hass: HomeAssistant, flow_client, mock_frontend) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Upper East Side"
    assert result["data"][CONF_LANGUAGE] == "en-us"


async def test_user_flow_invalid_url(hass: HomeAssistant, flow_client, mock_frontend) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {**USER_INPUT, CONF_MSN_URL: "https://www.msn.com/en-us/weather"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_MSN_URL: "invalid_url"}


async def test_user_flow_cannot_connect(hass: HomeAssistant, flow_client, mock_frontend) -> None:
    flow_client.async_get.side_effect = MsnWeatherError("HTTP 500")
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)
    assert result["errors"] == {"base": "cannot_connect"}


async def test_options_flow(hass: HomeAssistant, flow_client, mock_frontend) -> None:
    entry = MockConfigEntry(domain=DOMAIN, title="Upper East Side", data={
        CONF_NAME: "Upper East Side", CONF_LATITUDE: LAT, CONF_LONGITUDE: LON, CONF_LANGUAGE: "en-us",
    })
    entry.add_to_hass(hass)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    schema = result["data_schema"].schema
    defaults = {
        str(k): (k.default() if callable(k.default) else k.default)
        for k in schema if k.default is not vol_undefined()
    }
    defaults.update({CONF_LANGUAGE: "de-de", CONF_CYCLONE_RADIUS: 3000, CONF_CYCLONE_FOCUS: "nearest"})
    result = await hass.config_entries.options.async_configure(result["flow_id"], defaults)
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_LANGUAGE] == "de-de"
    assert entry.options[CONF_CYCLONE_RADIUS] == 3000
    assert CONF_API_KEY not in entry.options

    # the built-in key is not stored, an own key is
    for key, stored in ((DEFAULT_API_KEY, None), (" my-key ", "my-key")):
        result = await hass.config_entries.options.async_init(entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {**defaults, CONF_API_KEY: key}
        )
        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert entry.options.get(CONF_API_KEY) == stored


def _entry(hass: HomeAssistant, **kwargs) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Upper East Side",
        unique_id="40.774_-73.957_en-us",
        data={CONF_NAME: "Upper East Side", CONF_LATITUDE: LAT, CONF_LONGITUDE: LON, CONF_LANGUAGE: "en-us"},
        **kwargs,
    )
    entry.add_to_hass(hass)
    return entry


async def test_reconfigure(hass: HomeAssistant, flow_client, mock_frontend) -> None:
    entry = _entry(hass, options={CONF_CYCLONE_RADIUS: 100})
    result = await entry.start_reconfigure_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_NAME: "Midtown",
            CONF_USE_HOME: False,
            CONF_LOCATION: {CONF_LATITUDE: 40.75, CONF_LONGITUDE: -73.98},
        },
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.title == "Midtown"
    assert entry.unique_id == "40.750_-73.980_en-us"
    assert entry.data == {
        CONF_NAME: "Midtown", CONF_LATITUDE: 40.75, CONF_LONGITUDE: -73.98,
        CONF_LANGUAGE: "en-us", CONF_USE_HOME: False,
    }
    # the options are untouched
    assert entry.options == {CONF_CYCLONE_RADIUS: 100}


async def test_reconfigure_home_location(hass: HomeAssistant, flow_client, mock_frontend) -> None:
    hass.config.latitude, hass.config.longitude = 41.0, -73.0
    entry = _entry(hass)
    result = await entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_NAME: "Home", CONF_USE_HOME: True}
    )
    await hass.async_block_till_done()
    assert result["reason"] == "reconfigure_successful"
    assert (entry.data[CONF_LATITUDE], entry.data[CONF_LONGITUDE]) == (41.0, -73.0)
    assert entry.data[CONF_USE_HOME] is True


async def test_reconfigure_errors(hass: HomeAssistant, flow_client, mock_frontend) -> None:
    entry = _entry(hass)
    other = MockConfigEntry(
        domain=DOMAIN, title="Midtown", unique_id="40.750_-73.980_en-us",
        data={CONF_NAME: "Midtown", CONF_LATITUDE: 40.75, CONF_LONGITUDE: -73.98, CONF_LANGUAGE: "en-us"},
    )
    other.add_to_hass(hass)
    midtown = {CONF_USE_HOME: False, CONF_LOCATION: {CONF_LATITUDE: 40.75, CONF_LONGITUDE: -73.98}}

    result = await entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_USE_HOME: False, CONF_MSN_URL: "https://www.msn.com/en-us/weather"}
    )
    assert result["errors"] == {CONF_MSN_URL: "invalid_url"}

    flow_client.async_get.side_effect = MsnWeatherError("HTTP 500")
    result = await hass.config_entries.flow.async_configure(result["flow_id"], midtown)
    assert result["errors"] == {"base": "cannot_connect"}

    # another entry already uses that place
    flow_client.async_get.side_effect = None
    result = await hass.config_entries.flow.async_configure(result["flow_id"], midtown)
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert entry.data[CONF_LATITUDE] == LAT


def vol_undefined():
    import voluptuous as vol

    return vol.UNDEFINED


async def test_user_flow_home_location(hass: HomeAssistant, flow_client, mock_frontend) -> None:
    """Without changes the Home Assistant location is used and followed."""
    hass.config.latitude, hass.config.longitude = 40.0, -74.0
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_LANGUAGE: "en-us"})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert (result["data"][CONF_LATITUDE], result["data"][CONF_LONGITUDE]) == (40.0, -74.0)
    assert result["data"][CONF_USE_HOME] is True


async def test_user_flow_other_location(hass: HomeAssistant, flow_client, mock_frontend) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {**USER_INPUT, CONF_USE_HOME: False}
    )
    assert (result["data"][CONF_LATITUDE], result["data"][CONF_LONGITUDE]) == (LAT, LON)
    assert result["data"][CONF_USE_HOME] is False
