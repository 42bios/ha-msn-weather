"""Diagnostics do not leak the location."""

from __future__ import annotations

import json

from homeassistant.core import HomeAssistant

from custom_components.msn_weather.diagnostics import async_get_config_entry_diagnostics

from .conftest import LAT, LON
from .test_init import _setup


async def test_diagnostics(hass: HomeAssistant, mock_client, mock_frontend) -> None:
    entry = await _setup(hass)
    diag = await async_get_config_entry_diagnostics(hass, entry)
    text = json.dumps(diag, default=str)
    assert str(LAT) not in text and str(LON) not in text
    assert "Upper East Side" not in text and "test-secret" not in text
    assert diag["data"]["hourly"] > 100
    assert diag["data"]["storms"] == 2
