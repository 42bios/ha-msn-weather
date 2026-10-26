"""Map helpers: projection, storm track interpolation, imperial legends."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from custom_components.msn_weather.maps import (
    IMPERIAL_DISPLAY,
    NOWCAST_PALETTE,
    _fit_storm,
    _track_position,
    nowcast_slot,
    parse_nowcast,
    px_to_latlon,
    quadkey,
    storm_frame_times,
    world_px,
)

from .conftest import FIXTURES

T0 = datetime(2026, 10, 1, tzinfo=UTC)


def _point(hours: int, lon: float, lat: float, wind: float, forecast: bool = False) -> dict:
    return {
        "time": T0 + timedelta(hours=hours), "lon": lon, "lat": lat,
        "category": "TS", "max_wind": wind, "max_gust": None, "forecast": forecast,
    }


def test_quadkey() -> None:
    assert quadkey(3, 5, 3) == "213"


@pytest.mark.parametrize(("lat", "lon"), [(40.77, -73.95), (-33.9, 151.2), (0, 0)])
def test_projection_roundtrip(lat: float, lon: float) -> None:
    x, y = world_px(lat, lon, 6)
    lat2, lon2 = px_to_latlon(x, y, 6)
    assert lat2 == pytest.approx(lat, abs=1e-6)
    assert lon2 == pytest.approx(lon, abs=1e-6)


def test_track_position_interpolates() -> None:
    track = [_point(0, 10, 10, 50), _point(10, 20, 20, 100)]
    pos = _track_position(track, T0 + timedelta(hours=5))
    assert (pos["lon"], pos["lat"], pos["max_wind"]) == (15, 15, 75)
    assert _track_position(track, T0 - timedelta(hours=1)) == track[0]
    assert _track_position(track, T0 + timedelta(hours=20)) == track[-1]


def test_track_position_crosses_date_line() -> None:
    track = [_point(0, 179, 10, 50), _point(10, -179, 10, 50)]
    pos = _track_position(track, T0 + timedelta(hours=5))
    assert abs(pos["lon"]) == pytest.approx(180)


def test_storm_frame_times(storms) -> None:
    track = storms[0]["track"]
    now = next(p["time"] for p in track if p["forecast"])  # recorded data: pretend it is "now"
    times = storm_frame_times(storms[0], 12, now=now)
    assert len(times) == 12
    assert times == sorted(times)
    assert times[0] >= now - timedelta(hours=48)
    assert abs((times[-1] - track[-1]["time"]).total_seconds()) < 1
    assert storm_frame_times(storms[0], 1, now=now) == []
    assert storm_frame_times(None, 12) == []


def test_fit_storm(storms) -> None:
    for storm in storms:
        lat, lon, zoom = _fit_storm(storm, 800, 500)
        assert 2 <= zoom <= 6
        assert -90 < lat < 90 and -180 <= lon < 180


@pytest.mark.parametrize(
    ("unit", "metric", "imperial"),
    [("°C", 100, 212), ("km/h", 1.609344, 1), ("km", 1.609344, 1), ("hPa", 1013.25, 29.92), ("mm/h", 25.4, 1)],
)
def test_imperial_display(unit: str, metric: float, imperial: float) -> None:
    _, conv, back, legend = IMPERIAL_DISPLAY[unit]
    assert conv(metric) == pytest.approx(imperial, abs=0.01)
    assert back(conv(metric)) == pytest.approx(metric)
    assert list(legend) == sorted(legend)


def test_nowcast_slot() -> None:
    base = datetime(2026, 10, 18, 11, 52, tzinfo=UTC)
    assert nowcast_slot(base, base + timedelta(minutes=9), True) == base + timedelta(minutes=8)
    assert nowcast_slot(base, base - timedelta(minutes=9), False) == base - timedelta(minutes=8)
    assert nowcast_slot(base, base, True) == base


def test_parse_nowcast() -> None:
    shapes = parse_nowcast((FIXTURES / "nowcast_tile.json").read_bytes())
    assert shapes
    for ptype, level, polys in shapes:
        assert ptype in NOWCAST_PALETTE
        assert level in NOWCAST_PALETTE[ptype]
        assert all(len(ring) > 2 for poly in polys for ring in poly)
    assert parse_nowcast(b"") == []
    assert parse_nowcast(b'[{"type":"Feature","geometry":{"coordinates":[[[]]],"type":"MultiPolygon"},"properties":{"pType":0,"level":1}}]') == []


def test_legend_info() -> None:
    from custom_components.msn_weather.maps import MsnMapRenderer

    renderer = MsnMapRenderer(None, "key", "de-de")
    temp = renderer.legend_info("temperature")
    assert temp["type"] == "gradient" and temp["unit"] == "°C" and len(temp["stops"]) == 16
    assert temp["ticks"][0][0] == 0 and temp["ticks"][-1][0] == 1
    radar = renderer.legend_info("radar")
    assert radar["type"] == "swatches" and [r["label"] for r in radar["rows"]] == ["Regen", "Schnee", "Schneeregen"]
    renderer.imperial = True
    assert renderer.legend_info("temperature")["unit"] == "°F"
    assert renderer.legend_info("satellite") is None


def test_legend_levels() -> None:
    from custom_components.msn_weather.maps import MsnMapRenderer

    renderer = MsnMapRenderer(None, "key", "de-de")
    alerts = renderer.legend_info("alerts")
    assert alerts["type"] == "levels" and [i["label"] for i in alerts["items"]] == ["Gelb", "Orange", "Rot"]
    assert renderer.legend_info("lightning")["type"] == "levels"
