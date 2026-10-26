"""Parsing of the MSN responses (no Home Assistant needed)."""

from __future__ import annotations

import base64
from datetime import UTC, datetime
import json

import pytest

from custom_components.msn_weather.api import (
    compass,
    condition_from_symbol,
    extract_api_key,
    parse_calendar,
    parse_climate,
    parse_msn_url,
    parse_response,
    ticks_to_dt,
)

from .conftest import load


def test_parse_overview() -> None:
    data = parse_response(load("overview.json"))
    assert isinstance(data.current["temp"], (int, float))
    assert len(data.days) >= 10
    assert len(data.hourly) > 100
    assert data.insights, "weather detail texts missing"
    assert "umbrella" in data.life_today
    assert data.life_today["umbrella"]["hourly"], "hourly life index missing"
    assert data.day_details, "daily details missing"


def test_parse_storms(storms) -> None:
    assert len(storms) == 2
    for storm in storms:
        track = storm["track"]
        assert track == sorted(track, key=lambda p: p["time"])
        assert any(p["forecast"] for p in track)
        observed = [p for p in track if not p["forecast"]]
        # list values are mph – the integration takes km/h from the track
        assert storm["max_wind"] == observed[-1]["max_wind"]
        assert storm["closest_km"] <= storm["distance_km"]
    assert storms[0]["distance_km"] <= storms[1]["distance_km"]


def test_parse_climate_and_calendar() -> None:
    climate = parse_climate(load("weathertrends.json"))
    day = next(iter(climate["days"].values()))
    assert {"avg_high", "avg_low", "record_high", "record_low"} <= day.keys()
    assert climate["since"]
    calendar = parse_calendar(load("calendar.json"))
    assert len(calendar) >= 28
    assert {"date", "condition", "temp_high", "temp_low"} <= calendar[0].keys()


@pytest.mark.parametrize(
    ("symbol", "wx", "expected"),
    [
        ("d0000", None, "sunny"),
        ("n0000", None, "clear-night"),
        ("d2000", None, "partlycloudy"),
        ("d4000", None, "cloudy"),
        ("d4100", None, "rainy"),
        ("d4300", None, "pouring"),
        ("d4120", None, "snowy"),
        ("d4110", None, "snowy-rainy"),
        ("d4101", None, "lightning-rainy"),
        ("d4000", "FG", "fog"),
        (None, None, None),
    ],
)
def test_condition_from_symbol(symbol, wx, expected) -> None:
    assert condition_from_symbol(symbol, wx) == expected


def test_compass() -> None:
    assert compass(0, "en-us") == "N"
    assert compass(90, "de-de") == "O"
    assert compass(225, "en-us") == "SW"
    assert compass(None, "en-us") is None


def test_parse_msn_url() -> None:
    loc = base64.b64encode(json.dumps({"l": "New York", "x": "-73.95", "y": "40.77"}).encode()).decode()
    assert parse_msn_url(f"https://www.msn.com/en-us/weather/forecast/in-New-York?loc={loc}") == (
        40.77, -73.95, "New York",
    )
    assert parse_msn_url("https://www.msn.com/en-us/weather") is None


def test_ticks_to_dt() -> None:
    when = datetime(2026, 1, 1, tzinfo=UTC)
    ticks = int((when.replace(tzinfo=None) - datetime(1, 1, 1)).total_seconds() * 10**7)
    assert ticks_to_dt(ticks) == when


def test_extract_api_key() -> None:
    html = (
        'fetch("/weather/metadata/maps?ids=x&apiKey=AbCdEfGhIjKlMnOpQrStUvWxYz0123456789ab")'
        ' other&apiKey=AbCdEfGhIjKlMnOpQrStUvWxYz0123456789ab'
    )
    assert extract_api_key(html) == "AbCdEfGhIjKlMnOpQrStUvWxYz0123456789ab"
    assert extract_api_key("<html></html>") is None
