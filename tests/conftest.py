"""Shared fixtures: recorded MSN responses for New York (Upper East Side)."""

from __future__ import annotations

from collections.abc import Generator
import json
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.msn_weather.api import (
    parse_calendar,
    parse_climate,
    parse_response,
    parse_storms,
)

FIXTURES = Path(__file__).parent / "fixtures"
LAT, LON = 40.7736, -73.9566


def load(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text())


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Load custom_components/ in every test."""


@pytest.fixture
def storms() -> list[dict[str, Any]]:
    listing = load("hurricane_list.json")
    details = {
        f["id"]: load(f"hurricane_detail_{f['id']}.json")["features"]
        for f in listing["features"]
    }
    return parse_storms(listing, details, LAT, LON)


@pytest.fixture
def mock_client(storms: list[dict[str, Any]]) -> Generator[MagicMock]:
    """MsnWeatherClient returning the recorded responses."""
    with patch(
        "custom_components.msn_weather.coordinator.MsnWeatherClient", autospec=True
    ) as cls:
        client = cls.return_value
        client.api_key = "old-key"
        client.async_get = AsyncMock(side_effect=lambda: parse_response(load("overview.json")))
        client.async_get_storms = AsyncMock(return_value=storms)
        client.async_get_climate = AsyncMock(
            return_value=(
                parse_climate(load("weathertrends.json")),
                parse_calendar(load("calendar.json")),
            )
        )
        client.client_cls = cls
        yield client


@pytest.fixture
async def mock_frontend(hass) -> Generator[None]:
    """http / frontend are dependencies; the tests only need them to exist."""
    hass.http = MagicMock()
    hass.http.async_register_static_paths = AsyncMock()
    hass.config.components.update({"http", "frontend"})
    with patch("custom_components.msn_weather.add_extra_js_url"):
        yield
