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
    CONF_CYCLONE_FOCUS,
    CONF_CYCLONE_RADIUS,
    CONF_LANGUAGE,
    CONF_MSN_URL,
    CONF_USE_HOME,
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
