"""Renderer for MSN weather maps.

MSN delivers most weather layers as *data* tiles (JPEG/PNG whose pixels encode
values, with min/max stored in an 8px header) and colours them in the browser.
This module reproduces that: it downloads the data tiles, decodes and
interpolates the values, applies MSN's colour schemes and composes the result
with Bing map tiles (terrain shading, borders and labels).

No Home Assistant imports, so it can be tested standalone.
"""

from __future__ import annotations

import asyncio
import functools
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import io
import logging
import math
from pathlib import Path
import struct
import time
from typing import Any, Callable

import aiohttp
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .api import USER_AGENT

FONT_PATH = Path(__file__).parent / "fonts" / "DejaVuSans.ttf"

_LOGGER = logging.getLogger(__name__)

DATA_BASE = "https://assets.msn.com/weathermapdata/1/"
METADATA_URL = (
    "https://api.msn.com/weatherfalcon/weather/metadata/maps"
    "?ids=LatestAvailableVersions&ocid=msftweather&apiKey={api_key}"
)
BING = "https://t.ssl.ak.dynamic.tiles.virtualearth.net/comp/ch/{qk}?mkt={mkt}&og=2864&n=z&ur=IT"
# Full road map with hill shading and labels (background for overlay layers)
BING_ROAD = BING + "&it=G,L&shading=hill"
# Transparent hill shading + borders + water lines (drawn over heat maps)
BING_SHADING = (
    BING
    + "&it=Z,GF,L&shading=t&rs=1&dpi=d1&o=PNG&cstl=wr&shdw=1&jp=0"
    "&st=me|lv:0;v:0_pp|v:0_cp|v:0_wt|v:1_trs|v:1;lv:0;sc:FF6B6B6B;fc:FF6B6B6B;"
    "strokeWidthScale:0.2_cst|v:1;fc:FF000000;strokeWidthScale:0.5_cr|bv:1;"
    "bsc:f2000000;borderWidthScale:0.6_ad|bv:1;bsc:f2000000"
)
# Transparent labels and roads
BING_LABELS = BING + "&it=Z,GF,L&shading=hill&cstl=wr"
BING_AERIAL = "https://t.ssl.ak.tiles.virtualearth.net/tiles/a{qk}.jpeg?g=15639"

TILE = 256


# --------------------------------------------------------------------------
# Layer definitions
# --------------------------------------------------------------------------

ValueFn = Callable[..., Any]


def _linear(rgb: np.ndarray, mn: float, rng: float) -> tuple[np.ndarray, None]:
    return mn + rgb[..., 0] * rng / 255.0, None


def _wind(rgb: np.ndarray, mn: float, rng: float) -> tuple[np.ndarray, None]:
    u = mn + rgb[..., 0] * rng / 255.0
    v = mn + rgb[..., 1] * rng / 255.0
    return np.sqrt(u * u + v * v), None


def _precip(rgb: np.ndarray, mn: float, rng: float) -> tuple[np.ndarray, np.ndarray]:
    kind = np.floor(rgb[..., 1] / 64.0)
    r = np.where(kind == 3, 0.0, rgb[..., 0])
    d = (100.0 - (mn + r * rng / 255.0)) / 20.0
    rate = np.where(d <= 0, 1.0, np.where(d >= 5, 1e-5, np.power(10.0, -d))) * 3600.0
    rate = np.where(kind == 3, 0.0, rate)
    return rate, kind


def _snow(rgb: np.ndarray, mn: float, rng: float) -> tuple[np.ndarray, None]:
    return np.power(2.0, rgb[..., 0] * rng / 255.0 + mn) - 0.001, None


def _aqi(rgb: np.ndarray, mn: float, rng: float) -> tuple[np.ndarray, None]:
    r = np.where(rgb[..., 0] > 250, 255.0, rgb[..., 0])
    r = np.where(r < 5, 0.0, r)
    return r + (mn + rgb[..., 1] * rng / 255.0), None


@dataclass(frozen=True)
class MapLayer:
    key: str
    kind: str  # "grid" (encoded data), "overlay" (ready RGBA), "alerts"
    metadata: str
    background: str  # "heat" | "road" | "aerial"
    zooms: tuple[int, ...] = (5, 3)
    scenario: str | None = None
    fmt: str = "jpg"
    time_fmt: str | None = "%Y%m%d%H"
    time_step: int = 60  # minutes
    value_fn: ValueFn = _linear
    vmin: float = 0
    vmax: float = 1
    colors: tuple = ()
    # display conversion of the decoded value (for marker + legend)
    display: Callable[[float], float] = lambda v: v
    unit: str = ""
    legend: tuple[float, ...] = ()  # display values for legend ticks
    alpha_fn: Callable[[np.ndarray], np.ndarray] | None = None
    overlay_alpha: float = 1.0
    supports_forecast: bool = True
    extra: dict = field(default_factory=dict)


_TEMP_COLORS = (
    (0, 35, 20, 90), (0.1282, 60, 40, 130), (0.2564, 75, 60, 180), (0.3846, 90, 80, 190),
    (0.4701, 100, 100, 210), (0.5299, 115, 120, 220), (0.5641, 122, 151, 240),
    (0.5996, 148, 187, 235), (0.641, 49, 130, 126), (0.6838, 33, 132, 91),
    (0.7265, 60, 150, 86), (0.7692, 106, 173, 88), (0.812, 213, 180, 32),
    (0.8291, 240, 180, 10), (0.8974, 232, 77, 25), (0.9402, 165, 13, 7), (1, 100, 15, 0),
)

LAYERS: dict[str, MapLayer] = {
    "temperature": MapLayer(
        key="temperature", kind="grid", metadata="TileImageMetadata", background="heat",
        scenario="temperature", vmin=203, vmax=320, colors=_TEMP_COLORS,
        display=lambda v: v - 273.15, unit="°C", legend=(-20, -10, 0, 10, 20, 30, 40),
    ),
    "precipitation": MapLayer(
        key="precipitation", kind="grid", metadata="TileImageMetadata", background="road",
        scenario="precipimg", value_fn=_precip, vmin=0, vmax=20,
        colors=(
            (0, 121, 121, 121), (0.0018, 121, 121, 121), (0.02, 69, 82, 152),
            (0.1, 65, 165, 167), (0.15, 65, 141, 65), (0.3, 168, 168, 65),
            (0.48, 170, 126, 63), (0.6, 167, 65, 65), (1, 168, 65, 168),
        ),
        unit="mm/h", legend=(0.5, 5, 10, 15, 20),
        alpha_fn=lambda v: np.where(v < 0.1, 0.0, np.clip(0.55 + v / 4.0, 0.55, 0.85)),
    ),
    "wind": MapLayer(
        key="wind", kind="grid", metadata="TileImageMetadata", background="heat",
        scenario="windspeed", value_fn=_wind, vmin=0, vmax=104,
        colors=(
            (0, 173, 173, 173), (0.0096, 153, 213, 236), (0.0288, 105, 181, 209),
            (0.0481, 53, 144, 176), (0.0673, 111, 195, 102), (0.0865, 52, 144, 56),
            (0.1058, 9, 102, 32), (0.125, 227, 196, 71), (0.1442, 201, 169, 1),
            (0.1635, 151, 119, 0), (0.1827, 255, 179, 82), (0.2019, 235, 152, 41),
            (0.2308, 188, 104, 0), (0.2596, 157, 78, 0), (0.2788, 184, 80, 91),
            (0.3462, 137, 47, 59), (0.4423, 101, 32, 41), (0.4904, 53, 54, 150),
            (0.7404, 39, 38, 92), (1, 22, 21, 43),
        ),
        display=lambda v: v * 3.6, unit="km/h", legend=(0, 10, 20, 35, 55, 70, 100),
    ),
    "clouds": MapLayer(
        key="clouds", kind="overlay", metadata="Cloud", background="aerial",
        fmt="png", zooms=(6, 5), time_fmt="%Y%m%d%H%M", time_step=60,
    ),
    "humidity": MapLayer(
        key="humidity", kind="grid", metadata="TileImageMetadata", background="heat",
        scenario="humidity", vmin=0, vmax=100,
        colors=(
            (0, 173, 85, 56), (0.3, 173, 110, 56), (0.4, 173, 146, 56), (0.5, 105, 173, 56),
            (0.6, 56, 173, 121), (0.7, 56, 174, 173), (0.75, 56, 160, 173),
            (0.8, 56, 157, 173), (0.83, 56, 148, 173), (0.87, 56, 135, 173),
            (0.9, 56, 132, 173), (0.93, 56, 123, 173), (0.97, 56, 98, 157), (1, 56, 70, 114),
        ),
        unit="%", legend=(30, 50, 80, 90, 100),
    ),
    "visibility": MapLayer(
        key="visibility", kind="grid", metadata="TileImageMetadata", background="heat",
        scenario="visibility", vmin=0, vmax=20000,
        colors=(
            (0, 163, 89, 163), (0.08, 161, 89, 163), (0.11, 167, 86, 86), (0.25, 167, 86, 86),
            (0.3, 89, 97, 163), (0.4, 89, 101, 163), (0.45, 60, 188, 73),
            (0.75, 83, 167, 75), (1, 121, 121, 121),
        ),
        display=lambda v: v / 1000.0, unit="km", legend=(0.8, 2.7, 6, 16, 20),
    ),
    "pressure": MapLayer(
        key="pressure", kind="grid", metadata="TileImageMetadata", background="heat",
        scenario="pressure", vmin=90000, vmax=108000,
        colors=(
            (0, 8, 16, 48), (0.2778, 0, 32, 96), (0.4222, 0, 52, 146), (0.4778, 0, 90, 148),
            (0.5278, 0, 117, 146), (0.5667, 26, 140, 147), (0.5944, 103, 162, 155),
            (0.6181, 155, 183, 172), (0.6292, 182, 182, 182), (0.6403, 176, 174, 152),
            (0.6611, 167, 147, 107), (0.6889, 163, 116, 67), (0.7222, 159, 81, 44),
            (0.7667, 142, 47, 57), (0.8111, 111, 24, 64), (1, 48, 8, 24),
        ),
        display=lambda v: v / 100.0, unit="hPa", legend=(990, 1000, 1010, 1020, 1030),
    ),
    "dew_point": MapLayer(
        key="dew_point", kind="grid", metadata="TileImageMetadata", background="heat",
        scenario="dewpoint", vmin=203, vmax=320, colors=_TEMP_COLORS,
        display=lambda v: v - 273.15, unit="°C", legend=(-20, -10, 0, 10, 20, 30),
    ),
    "air_quality": MapLayer(
        key="air_quality", kind="grid", metadata="AqiForecastHeatMap", background="heat",
        zooms=(6, 3), time_fmt="%Y%m%d%H%M", value_fn=_aqi, vmin=0, vmax=500,
        colors=(
            (0, 235, 235, 235), (0.05, 0, 174, 86), (0.15, 255, 185, 0), (0.25, 242, 97, 12),
            (0.35, 209, 52, 56), (0.5, 136, 23, 152), (0.8, 110, 34, 15), (1, 110, 34, 15),
        ),
        unit="AQI", legend=(0, 50, 100, 150, 200, 300, 500),
        extra={"country": "eu"},
    ),
    "pollen": MapLayer(
        key="pollen", kind="grid", metadata="EuPollenHeatmap", background="heat",
        fmt="png", zooms=(5, 3), time_fmt=None, vmin=0, vmax=100,
        colors=(
            (0, 235, 235, 235), (0.03, 112, 171, 222), (0.15, 35, 193, 114),
            (0.38, 255, 214, 0), (0.68, 250, 141, 27), (0.88, 232, 74, 61), (1, 232, 74, 61),
        ),
        legend=(0, 25, 50, 75, 100), supports_forecast=False,
    ),
    "satellite": MapLayer(
        key="satellite", kind="overlay", metadata="SatellitePreRender", background="aerial",
        fmt="png", zooms=(6, 5), time_fmt=None, supports_forecast=False,
    ),
    "alerts": MapLayer(
        key="alerts", kind="alerts", metadata="SevereWeatherGeo", background="road",
        zooms=(5,), time_fmt=None, supports_forecast=False,
    ),
    "winter": MapLayer(
        key="winter", kind="grid", metadata="TileImageMetadata", background="road",
        scenario="snowfall", zooms=(5, 3), value_fn=_snow, vmin=0, vmax=500,
        colors=(
            (0, 121, 121, 121), (0.004, 69, 82, 152), (0.02, 65, 165, 167),
            (0.04, 65, 141, 65), (0.1, 168, 168, 65), (0.16, 170, 126, 63),
            (0.24, 167, 65, 65), (1, 168, 65, 168),
        ),
        unit="cm", legend=(1, 10, 20, 50, 100),
        alpha_fn=lambda v: np.where(v < 0.5, 0.0, 0.75),
        extra={"alerts_overlay": "WinterStormGeo"},
    ),
    "lightning": MapLayer(
        key="lightning", kind="lightning", metadata="LightningStrike", background="road",
        zooms=(4,), time_fmt=None, supports_forecast=False, unit="Blitze",
    ),
    "tropical_cyclones": MapLayer(
        key="tropical_cyclones", kind="cyclone", metadata="", background="aerial",
        zooms=(), time_fmt=None, supports_forecast=False,
    ),
    # minute-by-minute precipitation radar: vector polygons ("Sbn" nowcast), 4 minute steps
    "radar": MapLayer(
        key="radar", kind="nowcast", metadata="", background="road",
        zooms=(6, 4, 2), time_fmt=None, supports_forecast=False,
    ),
}

# Radar colours of msn.com: precipitation type (1 rain, 2 snow, 3 sleet) -> intensity level -> RGB.
# MSN uses the second palette for European markets.
_NOWCAST_LEVELS = (89, 105, 121, 137, 153, 169)


def _hex(c: str) -> tuple[int, int, int]:
    return int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)


NOWCAST_PALETTE = {
    1: dict(zip(_NOWCAST_LEVELS, map(_hex, ("#79b837", "#078f33", "#014b24", "#eec040", "#d05d2c", "#830826")))),
    2: dict(zip(_NOWCAST_LEVELS, map(_hex, ("#aae1e0", "#5ad2e0", "#249fdb", "#1547bd", "#101e96", "#01016e")))),
    3: dict(zip(_NOWCAST_LEVELS, map(_hex, ("#edb2c7", "#df71a9", "#bb338f", "#8a139b", "#660888", "#470765")))),
}
NOWCAST_PALETTE_EU = {
    1: dict(zip(_NOWCAST_LEVELS, map(_hex, ("#0000FF", "#00FF00", "#008C00", "#F9CD00", "#FF9C00", "#D20000")))),
    2: dict(zip(_NOWCAST_LEVELS, map(_hex, ("#85F0F7", "#65BEC7", "#4B949F", "#3D7F8B", "#2E6773", "#113948")))),
    3: dict(zip(_NOWCAST_LEVELS, map(_hex, ("#D4689D", "#CB5C93", "#BB4680", "#B03572", "#A42564", "#9F4F76")))),
}
_EU_MARKETS = {
    "au", "nz", "at", "be", "bg", "hr", "cy", "cz", "dk", "ee", "fi", "fr", "de", "gr", "hu", "ie", "it",
    "lv", "lt", "lu", "mt", "nl", "pl", "pt", "ro", "sk", "si", "es", "se", "kh", "th", "my", "la", "mm",
}
NOWCAST_STEP = timedelta(minutes=4)


def nowcast_slot(base: datetime, target: datetime, forward: bool) -> datetime:
    """Snap `target` to the 4 minute grid of a nowcast version."""
    steps = (target - base) / NOWCAST_STEP
    steps = int(steps) if forward else -int(-steps)
    return base + steps * NOWCAST_STEP


def parse_nowcast(raw: bytes) -> list[tuple[int, int, list]]:
    """MSN nowcast GeoJSON tile -> [(precip type, level, polygons as lon/lat rings)]."""
    import json

    try:
        features = json.loads(raw) if raw else []
    except ValueError:
        return []
    out = []
    for f in features or []:
        g, pr = f.get("geometry") or {}, f.get("properties") or {}
        coords = g.get("coordinates") or []
        polys = [coords] if g.get("type") == "Polygon" else coords if g.get("type") == "MultiPolygon" else []
        polys = [[ring for ring in poly if len(ring) > 2] for poly in polys]
        polys = [poly for poly in polys if poly]
        if polys:
            out.append((int(pr.get("pType") or 1), int(pr.get("level") or 0), polys))
    return out

STORM_COLORS = {
    "TD": (90, 160, 255), "TS": (60, 200, 120), "STS": (120, 220, 80),
    "H1": (255, 230, 80), "H2": (255, 170, 40), "H3": (255, 100, 40),
    "H4": (230, 40, 90), "H5": (180, 40, 200), "TY": (255, 120, 40), "STY": (200, 40, 160),
    "VST": (230, 40, 90), "VSTY": (230, 40, 90), "VSCS": (255, 100, 40), "SCS": (255, 170, 40),
    "CS": (120, 220, 80), "DD": (90, 160, 255), "D": (90, 160, 255), "SS": (60, 200, 120),
    "SD": (90, 160, 255),
}

ALERT_COLORS = {
    "Y": (241, 196, 15),
    "O": (230, 126, 34),
    "R": (231, 76, 60),
    "B": (52, 101, 164),
}


def _lut(colors: tuple) -> np.ndarray:
    """2049-step colour lookup table like MSN's colour mapper."""
    pos = np.array([c[0] for c in colors], dtype=np.float64)
    out = np.zeros((2049, 3), dtype=np.uint8)
    xs = np.linspace(0, 1, 2049)
    for ch in range(3):
        out[:, ch] = np.clip(np.round(np.interp(xs, pos, [c[ch + 1] for c in colors])), 0, 255)
    return out


# --------------------------------------------------------------------------
# Geometry helpers
# --------------------------------------------------------------------------


def world_px(lat: float, lon: float, zoom: int) -> tuple[float, float]:
    n = TILE * (2**zoom)
    s = min(max(math.sin(math.radians(lat)), -0.9999), 0.9999)
    x = (lon + 180.0) / 360.0 * n
    y = (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n
    return x, y


def quadkey(x: int, y: int, z: int) -> str:
    out = []
    for i in range(z, 0, -1):
        digit = 0
        mask = 1 << (i - 1)
        if x & mask:
            digit += 1
        if y & mask:
            digit += 2
        out.append(str(digit))
    return "".join(out)


def _header_minmax(arr: np.ndarray) -> tuple[float, float]:
    """Decode the float32 min/max stored in the 8px header row."""
    flat = arr.reshape(-1, arr.shape[2])
    width = arr.shape[1]

    def dec(p: np.ndarray) -> int:
        return ((int(p[0]) >> 6) << 6) + ((int(p[1]) >> 4) << 2) + (int(p[2]) >> 6)

    vals = []
    for base in (width * 3 + 3, width * 3 + 3 + 32):
        raw = bytes(dec(flat[base + i * 8]) for i in range(4))
        vals.append(struct.unpack("<f", raw)[0])
    return vals[0], vals[1]


def _paste_tile(target: Image.Image, raw: bytes | None, x: int, y: int, size: int = TILE) -> None:
    """Composite a map tile, scaled to ``size`` pixels if necessary."""
    if not raw:
        return
    try:
        im = Image.open(io.BytesIO(raw)).convert("RGBA")
    except (OSError, ValueError):
        return
    if im.size != (size, size):
        im = im.resize((size, size), Image.LANCZOS)
    target.alpha_composite(im, (x, y))


# --------------------------------------------------------------------------
# Renderer
# --------------------------------------------------------------------------


class _LRU(OrderedDict):
    def __init__(self, size: int) -> None:
        super().__init__()
        self.size = size

    def get_(self, key):
        if key in self:
            self.move_to_end(key)
            return self[key]
        return None

    def put(self, key, value) -> None:
        self[key] = value
        self.move_to_end(key)
        while len(self) > self.size:
            self.popitem(last=False)


@dataclass
class RenderResult:
    image: bytes
    valid_time: datetime | None
    value: float | None
    unit: str


# metric display unit -> (imperial unit, convert, back, legend in imperial units)
IMPERIAL_DISPLAY: dict[str, tuple[str, Callable[[float], float], Callable[[float], float], tuple]] = {
    "°C": ("°F", lambda v: v * 9 / 5 + 32, lambda v: (v - 32) * 5 / 9, (0, 20, 40, 60, 80, 100)),
    "mm/h": ("in/h", lambda v: v / 25.4, lambda v: v * 25.4, (0.02, 0.2, 0.4, 0.6, 0.8)),
    "km/h": ("mph", lambda v: v / 1.609344, lambda v: v * 1.609344, (0, 5, 10, 20, 35, 45, 60)),
    "km": ("mi", lambda v: v / 1.609344, lambda v: v * 1.609344, (0.5, 1.5, 4, 10, 12)),
    "hPa": ("inHg", lambda v: v / 33.8639, lambda v: v * 33.8639, (29.3, 29.6, 29.9, 30.2, 30.4)),
    "cm": ("in", lambda v: v / 2.54, lambda v: v * 2.54, (0.5, 4, 8, 20, 40)),
}


def px_to_latlon(x: float, y: float, zoom: int) -> tuple[float, float]:
    n = TILE * (2**zoom)
    lon = x / n * 360.0 - 180.0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    return lat, ((lon + 180.0) % 360.0) - 180.0


def _fit_storm(storm: dict, width: int, height: int, max_zoom: int = 6) -> tuple[float, float, int]:
    """Centre and zoom so that the storm's track and forecast cone fit into the image."""
    lon0 = storm["longitude"]
    coords = [(lon0, storm["latitude"])]
    for f in storm.get("features") or []:
        g = f.get("geometry") or {}
        c = g.get("coordinates") or []
        if g.get("type") == "Point":
            coords.append(tuple(c[:2]))
        elif g.get("type") == "LineString":
            coords += [tuple(p[:2]) for p in c]
        elif g.get("type") == "Polygon" and c:
            coords += [tuple(p[:2]) for p in c[0]]
    lons = [((x - lon0 + 180.0) % 360.0) - 180.0 + lon0 for x, _ in coords]  # unwrap date line
    lats = [y for _, y in coords]
    for zoom in range(max_zoom, 1, -1):
        x0, y0 = world_px(max(lats), min(lons), zoom)
        x1, y1 = world_px(min(lats), max(lons), zoom)
        if x1 - x0 <= width * 0.85 and y1 - y0 <= height * 0.8:
            break
    lat, lon = px_to_latlon((x0 + x1) / 2, (y0 + y1) / 2, zoom)
    return lat, lon, zoom


def _track_position(track: list[dict], when: datetime) -> dict | None:
    """Storm position at `when`, linearly interpolated between track points."""
    if not track:
        return None
    if when <= track[0]["time"]:
        return track[0]
    for a, b in zip(track, track[1:]):
        if a["time"] <= when <= b["time"]:
            span = (b["time"] - a["time"]).total_seconds() or 1
            f = (when - a["time"]).total_seconds() / span
            dlon = ((b["lon"] - a["lon"] + 180.0) % 360.0) - 180.0
            near = a if f < 0.5 else b
            return {
                "lon": a["lon"] + dlon * f,
                "lat": a["lat"] + (b["lat"] - a["lat"]) * f,
                "category": near["category"],
                "max_wind": (a["max_wind"] or 0) + ((b["max_wind"] or 0) - (a["max_wind"] or 0)) * f,
            }
    return track[-1]


def storm_frame_times(
    storm: dict | None, count: int, now: datetime | None = None
) -> list[datetime]:
    """Evenly spaced times from up to 2 days of history to the end of the forecast."""
    track = (storm or {}).get("track") or []
    if count < 2 or len(track) < 2:
        return []
    now = now or datetime.now(timezone.utc)
    start = max(track[0]["time"], now - timedelta(hours=48))
    end = track[-1]["time"]
    if end <= start:
        return []
    step = (end - start) / (count - 1)
    return [start + step * i for i in range(count)]


class MsnMapRenderer:
    """Fetches tiles and renders map images."""

    def __init__(
        self, session: aiohttp.ClientSession, api_key: str, language: str, imperial: bool = False,
    ) -> None:
        self._session = session
        self.imperial = imperial
        # draw title + legend into the images (off: the map card shows them itself)
        self.labels = True
        self._api_key = api_key
        self._mkt = language
        self._metadata: dict[str, Any] | None = None
        self._metadata_ts = 0.0
        self._bing = _LRU(800)
        self._data = _LRU(300)  # url -> (timestamp, bytes|None)
        self._lock = asyncio.Lock()
        self._sem = asyncio.Semaphore(8)
        # limit CPU-heavy composition so map rendering never starves Home Assistant
        self._cpu = asyncio.Semaphore(2)

    _TEXTS = {
        "de": {"no_storm": "kein aktiver Sturm", "disturbance": "Störung", "no_data": "keine Daten",
               "rain": "Regen", "snow": "Schnee", "sleet": "Schneeregen", "light": "leicht", "heavy": "stark", "yellow": "Gelb", "orange": "Orange", "red": "Rot"},
        "it": {"no_storm": "nessuna tempesta attiva", "disturbance": "Disturbo", "no_data": "nessun dato",
               "rain": "Pioggia", "snow": "Neve", "sleet": "Nevischio", "light": "debole", "heavy": "forte", "yellow": "Giallo", "orange": "Arancione", "red": "Rosso"},
        "en": {"no_storm": "no active storm", "disturbance": "Disturbance", "no_data": "no data",
               "rain": "Rain", "snow": "Snow", "sleet": "Sleet", "light": "light", "heavy": "heavy", "yellow": "Yellow", "orange": "Orange", "red": "Red"},
        "fr": {"no_storm": "aucune tempête active", "disturbance": "Perturbation", "no_data": "pas de données",
               "rain": "Pluie", "snow": "Neige", "sleet": "Neige fondue", "light": "faible", "heavy": "fort", "yellow": "Jaune", "orange": "Orange", "red": "Rouge"},
        "es": {"no_storm": "ninguna tormenta activa", "disturbance": "Perturbación", "no_data": "sin datos",
               "rain": "Lluvia", "snow": "Nieve", "sleet": "Aguanieve", "light": "débil", "heavy": "fuerte", "yellow": "Amarillo", "orange": "Naranja", "red": "Rojo"},
        "nl": {"no_storm": "geen actieve storm", "disturbance": "Storing", "no_data": "geen gegevens",
               "rain": "Regen", "snow": "Sneeuw", "sleet": "Natte sneeuw", "light": "licht", "heavy": "zwaar", "yellow": "Geel", "orange": "Oranje", "red": "Rood"},
    }

    def set_api_key(self, key: str) -> None:
        self._api_key = key
        self._metadata = None  # re-fetch with the new key

    def _tr(self, key: str) -> str:
        return self._TEXTS.get(self._mkt[:2], self._TEXTS["en"])[key]

    # -- networking ----------------------------------------------------------

    async def _get(self, url: str) -> bytes | None:
        async with self._sem:
            try:
                async with self._session.get(
                    url,
                    headers={"User-Agent": USER_AGENT, "Referer": "https://www.msn.com/"},
                    timeout=aiohttp.ClientTimeout(total=20),
                ) as resp:
                    if resp.status != 200:
                        return None
                    return await resp.read()
            except (aiohttp.ClientError, TimeoutError) as err:
                _LOGGER.debug("Tile request failed %s: %s", url, err)
                return None

    async def _bing_tile(self, template: str, x: int, y: int, z: int) -> bytes | None:
        url = template.format(qk=quadkey(x, y, z), mkt=self._mkt)
        cached = self._bing.get_(url)
        if cached is not None:
            return cached or None
        data = await self._get(url)
        self._bing.put(url, data or b"")
        return data

    async def _data_tile(self, url: str) -> bytes | None:
        cached = self._data.get_(url)
        if cached is not None and time.monotonic() - cached[0] < 1800:
            return cached[1]
        data = await self._get(url)
        self._data.put(url, (time.monotonic(), data))
        return data

    async def metadata(self) -> dict[str, Any]:
        async with self._lock:
            if self._metadata is None or time.monotonic() - self._metadata_ts > 600:
                raw = await self._get(METADATA_URL.format(api_key=self._api_key))
                if raw:
                    import json

                    try:
                        self._metadata = json.loads(raw)["value"][0]
                        self._metadata_ts = time.monotonic()
                    except (ValueError, KeyError, IndexError) as err:
                        _LOGGER.warning("Unexpected map metadata: %s", err)
            return self._metadata or {}

    # -- url building ---------------------------------------------------------

    def _template(self, meta: dict[str, Any], layer: MapLayer) -> tuple[str, str] | None:
        uris = (meta.get(layer.metadata) or {}).get("uris") or {}
        for version, url in uris.items():
            if url and url != "#":
                return version, url
        return None

    @staticmethod
    def _fill(template: str, **values: str) -> str:
        for k, v in values.items():
            template = template.replace("{" + k + "}", v)
        return template

    def _valid_time(self, layer: MapLayer, version: str, offset_h: int) -> datetime | None:
        if layer.time_fmt is None:
            return None
        now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        step = layer.time_step
        t = now.replace(minute=(now.minute // step) * step if step < 60 else 0)
        return t + timedelta(hours=offset_h)

    # -- rendering ------------------------------------------------------------

    async def render(
        self,
        layer_key: str,
        lat: float,
        lon: float,
        zoom: int = 7,
        width: int = 800,
        height: int = 500,
        offset_hours: int = 0,
        title: str | None = None,
        tz: Any = None,
        storms: list[dict] | None = None,
        shift_minutes: int = 0,
        scale: int = 1,
        storm_id: str | None = None,
        storm_time: datetime | None = None,
        nowcast_minutes: int = 0,
    ) -> RenderResult:
        layer = LAYERS[layer_key]
        meta = await self.metadata()
        tpl = self._template(meta, layer) if layer.metadata else None
        if not layer.supports_forecast:
            offset_hours = 0

        focus = None
        if layer.kind == "cyclone":
            active = [s for s in storms or [] if not s.get("disturbance") and s.get("latitude") is not None]
            focus = next((s for s in active if s.get("id") == storm_id), None) or (active[0] if active else None)
            if focus:
                lat, lon, zoom = _fit_storm(focus, width, height)
                if title:
                    title = f"{title}: {focus.get('name')} ({focus.get('category')})"
            else:
                lat, zoom = 20.0, 1

        # S = pixel density. With S = 2 the image has twice the pixels for the same
        # map extent ("retina"): Bing delivers 512 px tiles, data is sampled twice as fine.
        S = 2 if scale >= 2 else 1
        cx, cy = world_px(lat, lon, zoom)
        left, top = cx - width / 2, cy - height / 2
        css_zoom, css_left, css_top = zoom, left, top
        zoom = zoom + (S - 1)  # device-pixel zoom used for all data/overlay maths
        width, height, left, top = width * S, height * S, left * S, top * S

        # background tiles -> list of (x, y, size, job)
        hd = S == 2 and layer.background != "aerial"
        bg_tpl = {"heat": BING_SHADING, "road": BING_ROAD, "aerial": BING_AERIAL}[layer.background]
        if hd:
            tz_, tl, tt, tsize = css_zoom, css_left, css_top, TILE
            bg_tpl = bg_tpl if "dpi=d1" in bg_tpl else bg_tpl + "&rs=1&dpi=d1"
            lbl_tpl = BING_LABELS + "&rs=1&dpi=d1"
        else:
            tz_, tl, tt, tsize = zoom, left, top, TILE
            lbl_tpl = BING_LABELS
        cw, ch = width / (S if hd else 1), height / (S if hd else 1)
        grid = [
            (tx, ty)
            for tx in range(int(tl // tsize), int((tl + cw - 1) // tsize) + 1)
            for ty in range(int(tt // tsize), int((tt + ch - 1) // tsize) + 1)
        ]
        px_size = TILE * S if hd else TILE
        tiles = [
            (int(tx * px_size - left), int(ty * px_size - top), px_size) for tx, ty in grid
        ]
        n = 2**tz_
        bg_jobs = [self._bing_tile(bg_tpl, tx % n, ty, tz_) for tx, ty in grid]
        lbl_jobs = (
            [self._bing_tile(lbl_tpl, tx % n, ty, tz_) for tx, ty in grid]
            if layer.background != "road"
            else []
        )

        valid = None
        data_tiles: dict[tuple[int, int], bytes | None] = {}
        dzoom = None
        alerts: list[dict] = []
        points: list[dict] = []
        if layer.extra.get("alerts_overlay"):
            otpl = self._template(meta, MapLayer(key="", kind="", metadata=layer.extra["alerts_overlay"], background=""))
            if otpl:
                alerts = await self._load_alerts(otpl[1], lat, lon, zoom, left, top, width, height)
        if layer.kind == "lightning":
            points = await self._load_lightning(meta, zoom, left, top, width, height)
        elif layer.kind == "nowcast":
            points, valid = await self._load_nowcast(meta, zoom, left, top, width, height, nowcast_minutes)
        elif tpl:
            version, template = tpl
            valid = self._valid_time(layer, version, offset_hours)
            if layer.kind == "alerts":
                alerts = await self._load_alerts(template, lat, lon, zoom, left, top, width, height)
            else:
                candidates = (
                    [valid, valid + timedelta(hours=1), valid - timedelta(hours=1)]
                    if valid is not None
                    else [None]
                )
                for cand in candidates:
                    dzoom, data_tiles = await self._load_data(
                        layer, template, version, cand, zoom, left, top, width, height,
                        shift_minutes=shift_minutes,
                    )
                    if dzoom is not None:
                        valid = cand
                        break

        bg = await asyncio.gather(*bg_jobs)
        lbl = await asyncio.gather(*lbl_jobs)

        if valid is None and tpl and len(tpl[0]) == 12 and layer.kind == "overlay" and layer.time_fmt is None:
            try:
                valid = (
                    datetime.strptime(tpl[0], "%Y%m%d%H%M") - timedelta(minutes=shift_minutes)
                ).replace(tzinfo=timezone.utc)
            except ValueError:
                pass

        def _compose() -> tuple[bytes, float | None]:
            return self._compose(
                layer, zoom, left, top, width, height, tiles, bg, lbl,
                dzoom, data_tiles, alerts, valid, title, tz,
                points=points, storms=storms or [], focus=focus, s=S, storm_time=storm_time,
            )

        loop = asyncio.get_running_loop()
        async with self._cpu:
            image, value = await loop.run_in_executor(None, _compose)
        if layer.kind == "lightning":
            visible = 0
            for p in points:
                px, py = world_px(p["lat"], p["lon"], zoom)
                if left <= px <= left + width and top <= py <= top + height:
                    visible += 1
            value = float(visible)
        unit = layer.unit
        if self.imperial and unit in IMPERIAL_DISPLAY:
            unit, conv = IMPERIAL_DISPLAY[unit][0], IMPERIAL_DISPLAY[unit][1]
            value = conv(value) if value is not None and layer.kind != "lightning" else value
        return RenderResult(image=image, valid_time=valid, value=value, unit=unit)

    async def _load_nowcast(
        self, meta: dict[str, Any], zoom: int, left: float, top: float, width: int, height: int,
        minutes: int,
    ) -> tuple[list[dict], datetime | None]:
        """Radar polygons for now + `minutes` (negative = past), projected to image pixels."""
        def first(key: str) -> tuple[datetime, str] | None:
            uris = (meta.get(key) or {}).get("uris") or {}
            for version, url in uris.items():
                try:
                    return datetime.strptime(version, "%Y%m%d%H%M").replace(tzinfo=timezone.utc), url
                except ValueError:
                    continue
            return None

        forecast, history = first("NowcastVectorMap"), first("NowcastVectorMapHistory")
        if forecast is None:
            return [], None
        target = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        if target >= forecast[0] or history is None:
            when, template = nowcast_slot(forecast[0], max(target, forecast[0]), True), forecast[1]
        else:
            when, template = nowcast_slot(history[0], min(target, history[0]), False), history[1]
        stamp = when.strftime("%Y%m%d%H%M")
        dz = next((z for z in LAYERS["radar"].zooms if z <= zoom), 2)
        scale = 2 ** (zoom - dz)
        n = 2**dz
        xs = range(int(left / scale // TILE), int((left + width) / scale // TILE) + 1)
        ys = range(max(0, int(top / scale // TILE)), min(n - 1, int((top + height) / scale // TILE)) + 1)
        urls = [
            self._fill(template, x=str(x % n), y=str(y), z=str(dz), time=stamp).replace(".blc", ".json")
            for x in xs for y in ys
        ]
        raws = await asyncio.gather(*(self._data_tile(u) for u in urls))
        shapes = []
        for raw in raws:
            for ptype, level, polys in parse_nowcast(raw or b""):
                rings = [
                    [[(world_px(lat, lon, zoom)[0] - left, world_px(lat, lon, zoom)[1] - top) for lon, lat in ring]
                     for ring in poly]
                    for poly in polys
                ]
                shapes.append({"ptype": ptype, "level": level, "polys": rings})
        return shapes, when

    def _nowcast_overlay(self, shapes: list[dict], width: int, height: int) -> tuple[Image.Image, Image.Image]:
        """Coloured radar polygons (holes respected) and an index image of the levels."""
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        levels = Image.new("L", (width, height), 0)
        palette = NOWCAST_PALETTE_EU if self._mkt[-2:].lower() in _EU_MARKETS else NOWCAST_PALETTE
        for shape in sorted(shapes, key=lambda sh: sh["level"]):
            mask = Image.new("L", (width, height), 0)
            draw = ImageDraw.Draw(mask)
            for poly in shape["polys"]:
                draw.polygon(poly[0], fill=255)
                for hole in poly[1:]:
                    draw.polygon(hole, fill=0)
            level = min(_NOWCAST_LEVELS, key=lambda k: abs(k - shape["level"]))
            rgb = palette.get(shape["ptype"], palette[1])[level]
            img.paste(rgb + (205,), (0, 0, width, height), mask)
            # index image: precip type * 10 + intensity 1..6
            levels.paste(shape["ptype"] * 10 + _NOWCAST_LEVELS.index(level) + 1, (0, 0, width, height), mask)
        return img, levels

    async def _load_lightning(
        self, meta: dict[str, Any], zoom: int, left: float, top: float, width: int, height: int,
    ) -> list[dict]:
        """Lightning strikes of the last ~2 hours (current + history files)."""
        import json

        templates = []
        for key in ("LightningStrike", "LightningStrikeHistory"):
            for url in ((meta.get(key) or {}).get("uris") or {}).values():
                if url and url != "#":
                    templates.append(url)
        dz = 4
        scale = 2 ** (zoom - dz)
        xs = range(int(left / scale // TILE), int((left + width) / scale // TILE) + 1)
        ys = range(int(top / scale // TILE), int((top + height) / scale // TILE) + 1)
        n = 2**dz
        urls = [
            self._fill(t, x=str(x % n), y=str(y), z=str(dz), dataVersion="1")
            for t in templates for x in xs for y in ys
        ]
        raws = await asyncio.gather(*(self._data_tile(u) for u in urls))
        seen: set = set()
        points = []
        for raw in raws:
            if not raw:
                continue
            try:
                feats = json.loads(raw).get("features", [])
            except ValueError:
                continue
            for f in feats:
                try:
                    lon, lat = f["geometry"]["coordinates"][:2]
                    ts = f["properties"]["start_time"] / 1000.0
                except (KeyError, TypeError, ValueError):
                    continue
                key = (round(lon, 4), round(lat, 4), int(ts))
                if key in seen:
                    continue
                seen.add(key)
                points.append({"lat": lat, "lon": lon, "time": ts, "type": f["properties"].get("type")})
        return points

    async def _load_data(
        self, layer: MapLayer, template: str, version: str, valid: datetime | None,
        zoom: int, left: float, top: float, width: int, height: int,
        shift_minutes: int = 0,
    ) -> tuple[int | None, dict[tuple[int, int], bytes | None]]:
        values = {"format": layer.fmt, "version": version}
        if layer.scenario:
            values["scenario"] = layer.scenario
        values.update(layer.extra)
        if valid is not None and layer.time_fmt:
            values["time"] = valid.strftime(layer.time_fmt)
        else:
            values["time"] = version
            if shift_minutes and len(version) == 12:
                try:
                    shifted = datetime.strptime(version, "%Y%m%d%H%M") - timedelta(minutes=shift_minutes)
                    values["time"] = shifted.strftime("%Y%m%d%H%M")
                except ValueError:
                    pass

        for dz in layer.zooms:
            if dz > zoom and dz != layer.zooms[-1]:
                continue
            scale = 2 ** (zoom - dz)
            x0 = int(math.floor((left / scale - 1) / TILE))
            x1 = int(math.floor(((left + width) / scale + 1) / TILE))
            y0 = int(math.floor((top / scale - 1) / TILE))
            y1 = int(math.floor(((top + height) / scale + 1) / TILE))
            n = 2**dz
            coords = [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1) if 0 <= y < n]
            urls = [
                self._fill(template, x=str(x % n), y=str(y), z=str(dz), **values)
                for x, y in coords
            ]
            results = await asyncio.gather(*(self._data_tile(u) for u in urls))
            if any(results):
                return dz, dict(zip(coords, results))
        return None, {}

    async def _load_alerts(
        self, template: str, lat: float, lon: float, zoom: int,
        left: float, top: float, width: int, height: int,
    ) -> list[dict]:
        import json

        dz = 5
        scale = 2 ** (zoom - dz)
        xs = range(int(left / scale // TILE), int((left + width) / scale // TILE) + 1)
        ys = range(int(top / scale // TILE), int((top + height) / scale // TILE) + 1)
        urls = [self._fill(template, x=str(x), y=str(y), z=str(dz)) for x in xs for y in ys]
        raws = await asyncio.gather(*(self._data_tile(u) for u in urls))
        features: dict[str, dict] = {}
        for raw in raws:
            if not raw:
                continue
            try:
                for f in json.loads(raw).get("features", []):
                    features[f.get("properties", {}).get("id") or str(len(features))] = f
            except ValueError:
                continue
        return list(features.values())

    # -- composition (runs in executor) ---------------------------------------

    def _compose(
        self, layer: MapLayer, zoom: int, left: float, top: float, width: int, height: int,
        tiles, bg, lbl, dzoom, data_tiles, alerts, valid, title, tz,
        points=(), storms=(), focus=None, s: int = 1, storm_time: datetime | None = None,
    ) -> tuple[bytes, float | None]:
        canvas = Image.new("RGBA", (width, height), (230, 230, 230, 255))
        bg_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        for (x, y, size), raw in zip(tiles, bg):
            _paste_tile(bg_layer, raw, x, y, size)

        value_at_center = None
        label = None
        if layer.kind == "grid" and dzoom is not None:
            values, aux = self._sample(layer, zoom, dzoom, left, top, width, height, data_tiles)
            lut = _lut(layer.colors)
            idx = np.clip(
                np.round((values - layer.vmin) / (layer.vmax - layer.vmin) * 2048), 0, 2048
            ).astype(np.int32)
            rgb = lut[np.nan_to_num(idx, nan=0).astype(np.int32)]
            alpha = np.full(values.shape, 255.0)
            if layer.alpha_fn is not None:
                alpha = layer.alpha_fn(values) * 255.0
            alpha = np.where(np.isnan(values), 0, alpha)
            color = Image.fromarray(
                np.dstack([rgb, alpha.astype(np.uint8)]).astype(np.uint8), "RGBA"
            )
            cv = values[height // 2, width // 2]
            if not np.isnan(cv):
                value_at_center = float(layer.display(float(cv)))
            if layer.background == "heat":
                canvas.alpha_composite(color)
                canvas.alpha_composite(bg_layer)
            else:
                canvas.alpha_composite(bg_layer)
                canvas.alpha_composite(color)
            if alerts:
                canvas.alpha_composite(self._alerts_overlay(alerts, zoom, left, top, width, height))
        elif layer.kind == "overlay" and dzoom is not None:
            canvas.alpha_composite(bg_layer)
            overlay = self._overlay(zoom, dzoom, left, top, width, height, data_tiles)
            canvas.alpha_composite(overlay)
        elif layer.kind == "alerts":
            canvas.alpha_composite(bg_layer)
            canvas.alpha_composite(self._alerts_overlay(alerts, zoom, left, top, width, height))
        elif layer.kind == "lightning":
            canvas.alpha_composite(bg_layer)
            canvas.alpha_composite(self._lightning_overlay(points, zoom, left, top, width, height, s))
        elif layer.kind == "nowcast":
            canvas.alpha_composite(bg_layer)
            radar, levels = self._nowcast_overlay(points, width, height)
            canvas.alpha_composite(radar)
            code = levels.getpixel((width // 2, height // 2))
            if code:
                value_at_center = float(code % 10)  # intensity 1 (light) .. 6 (heavy)
                label = f"{self._tr({1: 'rain', 2: 'snow', 3: 'sleet'}.get(code // 10, 'rain'))} {code % 10}/6"
        elif layer.kind == "cyclone":
            canvas.alpha_composite(bg_layer)
            canvas.alpha_composite(self._storm_overlay(
                storms, zoom, left, top, width, height, s,
                focus_id=focus.get("id") if focus else None, storm_time=storm_time,
            ))
            if storm_time is not None and focus is not None:
                valid = storm_time
        else:
            canvas.alpha_composite(bg_layer)

        for (x, y, size), raw in zip(tiles, lbl):
            _paste_tile(canvas, raw, x, y, size)

        no_data = dzoom is None and layer.kind == "grid" or (layer.kind == "overlay" and dzoom is None)
        if layer.kind == "cyclone" and focus is None:
            title = (title or "") + " – " + self._tr("no_storm")
        self._decorate(
            canvas, layer, value_at_center, valid, title, tz, no_data,
            marker=layer.kind != "cyclone" or focus is None, s=s, label=label,
        )
        buf = io.BytesIO()
        canvas.convert("RGB").save(buf, format="PNG", optimize=True)
        return buf.getvalue(), value_at_center

    def _sample(
        self, layer: MapLayer, zoom: int, dzoom: int, left: float, top: float,
        width: int, height: int, data_tiles: dict,
    ) -> tuple[np.ndarray, np.ndarray | None]:
        xs = [c[0] for c in data_tiles]
        ys = [c[1] for c in data_tiles]
        x0, y0 = min(xs), min(ys)
        mw, mh = (max(xs) - x0 + 1) * TILE, (max(ys) - y0 + 1) * TILE
        mosaic = np.full((mh, mw), np.nan, dtype=np.float32)
        for (tx, ty), raw in data_tiles.items():
            if not raw:
                continue
            try:
                arr = np.asarray(Image.open(io.BytesIO(raw)).convert("RGBA"))
            except (OSError, ValueError):
                continue
            if arr.shape[0] < 9 + TILE or arr.shape[1] < 1 + TILE:
                continue
            mn, mx = _header_minmax(arr)
            data = arr[9 : 9 + TILE, 1 : 1 + TILE, :3].astype(np.float32)
            vals, _ = layer.value_fn(data, mn, mx - mn)
            oy, ox = (ty - y0) * TILE, (tx - x0) * TILE
            mosaic[oy : oy + TILE, ox : ox + TILE] = vals

        scale = 2 ** (zoom - dzoom)
        gx = (left + np.arange(width) + 0.5) / scale - 0.5 - x0 * TILE
        gy = (top + np.arange(height) + 0.5) / scale - 0.5 - y0 * TILE
        gx = np.clip(gx, 0, mw - 1.001)
        gy = np.clip(gy, 0, mh - 1.001)
        ix, iy = np.floor(gx).astype(int), np.floor(gy).astype(int)
        fx, fy = (gx - ix)[None, :], (gy - iy)[:, None]
        ix1, iy1 = np.minimum(ix + 1, mw - 1), np.minimum(iy + 1, mh - 1)
        a = mosaic[iy[:, None], ix[None, :]]
        b = mosaic[iy[:, None], ix1[None, :]]
        c = mosaic[iy1[:, None], ix[None, :]]
        d = mosaic[iy1[:, None], ix1[None, :]]
        out = (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy
        return out, None

    def _overlay(
        self, zoom: int, dzoom: int, left: float, top: float, width: int, height: int,
        data_tiles: dict,
    ) -> Image.Image:
        xs = [c[0] for c in data_tiles]
        ys = [c[1] for c in data_tiles]
        x0, y0 = min(xs), min(ys)
        mosaic = Image.new(
            "RGBA", ((max(xs) - x0 + 1) * TILE, (max(ys) - y0 + 1) * TILE), (0, 0, 0, 0)
        )
        for (tx, ty), raw in data_tiles.items():
            if raw:
                try:
                    im = Image.open(io.BytesIO(raw)).convert("RGBA")
                    if im.size != (TILE, TILE):
                        im = im.crop((0, 0, TILE, TILE))
                    mosaic.paste(im, ((tx - x0) * TILE, (ty - y0) * TILE))
                except (OSError, ValueError):
                    pass
        scale = 2 ** (zoom - dzoom)
        box = (
            left / scale - x0 * TILE,
            top / scale - y0 * TILE,
            (left + width) / scale - x0 * TILE,
            (top + height) / scale - y0 * TILE,
        )
        return mosaic.resize((width, height), Image.BILINEAR, box=box)

    def _lightning_overlay(
        self, points: list[dict], zoom: int, left: float, top: float, width: int, height: int,
        s: int = 1,
    ) -> Image.Image:
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img, "RGBA")
        now = time.time()
        for p in sorted(points, key=lambda p: p["time"]):
            x, y = world_px(p["lat"], p["lon"], zoom)
            x, y = x - left, y - top
            if not (-5 <= x <= width + 5 and -5 <= y <= height + 5):
                continue
            age = (now - p["time"]) / 60.0
            if age < 10:
                col, r = (255, 255, 120, 255), 5 * s
            elif age < 30:
                col, r = (255, 170, 0, 240), 4 * s
            elif age < 60:
                col, r = (230, 70, 30, 220), 3 * s
            else:
                col, r = (150, 30, 60, 180), 3 * s
            if p.get("type") == "CloudToGround":
                draw.line((x - r, y, x + r, y), fill=col, width=2 * s)
                draw.line((x, y - r, x, y + r), fill=col, width=2 * s)
            else:
                draw.ellipse((x - r + 1, y - r + 1, x + r - 1, y + r - 1), fill=col)
        return img

    def _storm_overlay(
        self, storms: list[dict], zoom: int, left: float, top: float, width: int, height: int,
        s: int = 1, focus_id: str | None = None, storm_time: datetime | None = None,
    ) -> Image.Image:
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img, "RGBA")
        font = self._font(14 * s)

        def pt(lon, lat):
            x, y = world_px(lat, lon, zoom)
            # wrap around the date line towards the view
            world = TILE * 2**zoom
            while x - left < -world / 2:
                x += world
            while x - left > width + world / 2:
                x -= world
            return x - left, y - top

        for storm in storms:
            feats = storm.get("features") or []
            for f in feats:
                g, pr = f.get("geometry") or {}, f.get("properties") or {}
                if g.get("type") == "Polygon" and g.get("coordinates"):
                    draw.polygon([pt(*c[:2]) for c in g["coordinates"][0]], fill=(255, 255, 255, 55), outline=(255, 255, 255, 160))
            for f in feats:
                g, pr = f.get("geometry") or {}, f.get("properties") or {}
                if g.get("type") == "LineString":
                    pts = [pt(*c[:2]) for c in g["coordinates"]]
                    if pr.get("dataType") == "Forecast":
                        for a, b in zip(pts[::1], pts[1:]):
                            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
                            draw.line((a[0], a[1], mx, my), fill=(255, 255, 255, 230), width=2 * s)
                    else:
                        draw.line(pts, fill=(200, 200, 200, 220), width=3 * s)
            for f in feats:
                g, pr = f.get("geometry") or {}, f.get("properties") or {}
                if g.get("type") != "Point":
                    continue
                x, y = pt(*g["coordinates"][:2])
                col = STORM_COLORS.get(pr.get("category") or "", (200, 200, 200)) + (255,)
                r = (7 if pr.get("dataType") == "Current" else 4) * s
                draw.ellipse((x - r, y - r, x + r, y + r), fill=col, outline=(0, 0, 0, 200))
            moving = storm_time is not None and storm.get("id") == focus_id
            if moving and (pos := _track_position(storm.get("track") or [], storm_time)):
                x, y = pt(pos["lon"], pos["lat"])
                col = STORM_COLORS.get(pos["category"], (200, 200, 200))
                r = 13 * s
                # cyclone symbol: coloured disc, white eye and two spiral arms
                draw.ellipse((x - r * 1.6, y - r * 1.6, x + r * 1.6, y + r * 1.6), fill=col + (70,))
                draw.arc((x - r * 1.5, y - r, x + r * 0.5, y + r), 180, 330, fill=col + (255,), width=4 * s)
                draw.arc((x - r * 0.5, y - r, x + r * 1.5, y + r), 0, 150, fill=col + (255,), width=4 * s)
                draw.ellipse((x - r * 0.75, y - r * 0.75, x + r * 0.75, y + r * 0.75), fill=col + (255,), outline=(0, 0, 0, 200), width=s)
                draw.ellipse((x - r * 0.25, y - r * 0.25, x + r * 0.25, y + r * 0.25), fill=(255, 255, 255, 255))
                label = f"{storm.get('name')} · {pos['category']} · {self._wind(pos['max_wind'])}"
                tw = draw.textlength(label, font=font)
                draw.rounded_rectangle((x + 18 * s, y - 12 * s, x + 30 * s + tw, y + 12 * s), 6 * s, fill=(30, 30, 30, 220))
                draw.text((x + 24 * s, y - 8 * s), label, font=font, fill=(255, 255, 255, 255))
                continue
            if storm.get("latitude") is not None:
                x, y = pt(storm["longitude"], storm["latitude"])
                if storm.get("disturbance"):
                    d6 = 6 * s
                    draw.line((x - d6, y - d6, x + d6, y + d6), fill=(255, 80, 80, 255), width=3 * s)
                    draw.line((x - d6, y + d6, x + d6, y - d6), fill=(255, 80, 80, 255), width=3 * s)
                    label = self._tr("disturbance")
                else:
                    label = f"{storm.get('name')} · {storm.get('category')} · {self._wind(storm.get('max_wind'))}"
                if -50 < x < width + 50 and -20 < y < height + 20:
                    tw = draw.textlength(label, font=font)
                    draw.rounded_rectangle((x + 10 * s, y - 12 * s, x + 22 * s + tw, y + 12 * s), 6 * s, fill=(30, 30, 30, 210))
                    draw.text((x + 16 * s, y - 8 * s), label, font=font, fill=(255, 255, 255, 255))
        return img

    def _wind(self, kmh: float | None) -> str:
        if self.imperial:
            return f"{(kmh or 0) / 1.609344:.0f} mph"
        return f"{kmh or 0:.0f} km/h"

    def _alerts_overlay(
        self, features: list[dict], zoom: int, left: float, top: float, width: int, height: int,
    ) -> Image.Image:
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img, "RGBA")
        now = time.time()
        order = {"B": 0, "Y": 1, "O": 2, "R": 3}

        def level(f: dict) -> str | None:
            best = None
            for w in f.get("properties", {}).get("warnings", []):
                try:
                    if not int(w.get("init_time", 0)) <= now + 86400 or int(w.get("expire_time", 0)) < now:
                        continue
                except ValueError:
                    continue
                lv = w.get("fs0")
                if lv in order and (best is None or order[lv] > order[best]):
                    best = lv
            return best

        def project(ring):
            return [
                (world_px(lat, lon, zoom)[0] - left, world_px(lat, lon, zoom)[1] - top)
                for lon, lat in ring
            ]

        items = [(level(f), f) for f in features]
        for lv, f in sorted((i for i in items if i[0]), key=lambda i: order[i[0]]):
            geom = f.get("geometry", {})
            polys = (
                [geom.get("coordinates", [])]
                if geom.get("type") == "Polygon"
                else geom.get("coordinates", []) if geom.get("type") == "MultiPolygon" else []
            )
            r, g, b = ALERT_COLORS.get(lv, (200, 200, 200))
            for poly in polys:
                if poly and len(poly[0]) > 2:
                    pts = project(poly[0])
                    draw.polygon(pts, fill=(r, g, b, 150), outline=(r, g, b, 230))
        return img

    # -- decoration ------------------------------------------------------------

    @staticmethod
    @functools.lru_cache(maxsize=16)
    def _font(size: int):
        # Bundled DejaVu Sans: Pillow's built-in font has no umlauts / accents.
        try:
            return ImageFont.truetype(str(FONT_PATH), size)
        except OSError:
            pass
        try:
            return ImageFont.load_default(size=size)
        except TypeError:
            return ImageFont.load_default()

    def _decorate(
        self, canvas: Image.Image, layer: MapLayer, value: float | None,
        valid: datetime | None, title: str | None, tz: Any, no_data: bool,
        marker: bool = True, s: int = 1, label: str | None = None,
    ) -> None:
        draw = ImageDraw.Draw(canvas, "RGBA")
        w, h = canvas.size
        cx, cy = w // 2, h // 2

        # location marker
        if marker:
            draw.ellipse((cx - 7 * s, cy - 7 * s, cx + 7 * s, cy + 7 * s), fill=(255, 255, 255, 255))
            draw.ellipse((cx - 5 * s, cy - 5 * s, cx + 5 * s, cy + 5 * s), fill=(255, 196, 0, 255))

        font = self._font(15 * s)
        small = self._font(12 * s)

        unit, conv, back, legend = layer.unit, (lambda v: v), (lambda v: v), layer.legend
        if self.imperial and layer.unit in IMPERIAL_DISPLAY:
            unit, conv, back, legend = IMPERIAL_DISPLAY[layer.unit]
        txt = label
        if txt is None and value is not None and layer.kind != "nowcast":
            value = conv(value)
            if unit == "inHg":
                txt = f"{value:.2f} {unit}"
            elif abs(value) >= 10 or unit in ("°C", "°F", "%", "AQI", "hPa"):
                txt = f"{value:.0f} {unit}"
            else:
                txt = f"{value:.1f} {unit}"
        if txt:
            tw = draw.textlength(txt, font=font)
            bx, by = cx + 12 * s, cy - 30 * s
            draw.rounded_rectangle((bx, by, bx + tw + 16 * s, by + 26 * s), 6 * s, fill=(40, 40, 40, 220))
            draw.text((bx + 8 * s, by + 5 * s), txt, font=font, fill=(255, 255, 255, 255))

        # title + time
        parts = [title] if title else []
        if valid is not None:
            local = valid.astimezone(tz) if tz else valid
            fmt = {"de": "%d.%m. %H:%M", "it": "%d/%m %H:%M", "fr": "%d/%m %H:%M", "es": "%d/%m %H:%M", "nl": "%d-%m %H:%M"}
            parts.append(local.strftime(fmt.get(self._mkt[:2], "%b %d, %H:%M")))
        if no_data:
            parts.append(self._tr("no_data"))
        if parts and self.labels:
            txt = "  ·  ".join(parts)
            tw = draw.textlength(txt, font=font)
            draw.rounded_rectangle((10 * s, 10 * s, 30 * s + tw, 38 * s), 8 * s, fill=(255, 255, 255, 230))
            draw.text((20 * s, 16 * s), txt, font=font, fill=(30, 30, 30, 255))

        # legend
        if layer.colors and layer.legend and self.labels:
            lw, lh = min(320 * s, w - 40 * s), 12 * s
            lx, ly = w - lw - 14 * s, h - 40 * s
            uw = draw.textlength(unit, font=small) + 8 * s if unit else 0  # unit label inside the box
            draw.rounded_rectangle((lx - 8 * s - uw, ly - 6 * s, lx + lw + 8 * s, ly + lh + 22 * s), 8 * s, fill=(255, 255, 255, 220))
            lut = _lut(layer.colors)
            inv = self._inverse_display(layer)
            dvals = legend
            raw = [inv(back(v)) for v in dvals]
            lo, hi = min(raw), max(raw)
            for i in range(lw):
                rv = lo + (hi - lo) * i / max(1, lw - 1)
                k = int(np.clip(round((rv - layer.vmin) / (layer.vmax - layer.vmin) * 2048), 0, 2048))
                draw.line((lx + i, ly, lx + i, ly + lh), fill=tuple(int(c) for c in lut[k]) + (255,))
            for dv, rv in zip(dvals, raw):
                px = lx + (rv - lo) / (hi - lo or 1) * (lw - 1)
                label = f"{dv:g}"
                tw = draw.textlength(label, font=small)
                draw.text((min(max(px - tw / 2, lx), lx + lw - tw), ly + lh + 3 * s), label, font=small, fill=(40, 40, 40, 255))
            if unit:
                draw.text((lx - uw, ly), unit, font=small, fill=(40, 40, 40, 255))

        if layer.kind == "nowcast" and self.labels:
            palette = NOWCAST_PALETTE_EU if self._mkt[-2:].lower() in _EU_MARKETS else NOWCAST_PALETTE
            sw, sh, gap = 16 * s, 10 * s, 4 * s
            names = [self._tr(k) for k in ("rain", "snow", "sleet")]
            nw = max(draw.textlength(n, font=small) for n in names) + 8 * s
            lw = nw + 6 * sw
            lx, ly = w - lw - 16 * s, h - 3 * (sh + gap) - 26 * s
            draw.rounded_rectangle((lx - 8 * s, ly - 6 * s, lx + lw + 8 * s, h - 10 * s), 8 * s, fill=(255, 255, 255, 220))
            for row, (ptype, name) in enumerate(zip((1, 2, 3), names)):
                y = ly + row * (sh + gap)
                draw.text((lx, y - 2 * s), name, font=small, fill=(40, 40, 40, 255))
                for i, level in enumerate(_NOWCAST_LEVELS):
                    x = lx + nw + i * sw
                    draw.rectangle((x, y, x + sw - 1, y + sh), fill=palette[ptype][level] + (255,))
            y = ly + 3 * (sh + gap)
            draw.text((lx + nw, y), self._tr("light"), font=small, fill=(40, 40, 40, 255))
            heavy = self._tr("heavy")
            draw.text((lx + lw - draw.textlength(heavy, font=small), y), heavy, font=small, fill=(40, 40, 40, 255))

        att = "© Microsoft, TomTom"
        draw.text((10 * s, h - 18 * s), att, font=self._font(11 * s), fill=(60, 60, 60, 255))

    def legend_info(self, layer_key: str) -> dict[str, Any] | None:
        """Legend of a layer for the map card: gradient stops / radar swatches with labels."""
        layer = LAYERS[layer_key]
        hexc = lambda c: "#%02x%02x%02x" % tuple(int(v) for v in c[:3])  # noqa: E731
        if layer.kind == "nowcast":
            palette = NOWCAST_PALETTE_EU if self._mkt[-2:].lower() in _EU_MARKETS else NOWCAST_PALETTE
            return {
                "type": "swatches",
                "rows": [
                    {"label": self._tr(name), "colors": [hexc(palette[ptype][lv]) for lv in _NOWCAST_LEVELS]}
                    for ptype, name in ((1, "rain"), (2, "snow"), (3, "sleet"))
                ],
                "low": self._tr("light"),
                "high": self._tr("heavy"),
            }
        if layer.kind == "alerts":
            return {"type": "levels", "items": [
                {"label": self._tr(k), "color": hexc(ALERT_COLORS[c])} for k, c in (("yellow", "Y"), ("orange", "O"), ("red", "R"))
            ]}
        if layer.kind == "lightning":
            return {"type": "levels", "items": [
                {"label": label, "color": color} for label, color in (
                    ("< 10 min", "#ffff78"), ("< 30 min", "#ffaa00"), ("< 60 min", "#e6461e"), ("> 60 min", "#961e3c"))
            ]}
        if not (layer.colors and layer.legend):
            return None
        unit, back, legend = layer.unit, (lambda v: v), layer.legend
        if self.imperial and layer.unit in IMPERIAL_DISPLAY:
            unit, _, back, legend = IMPERIAL_DISPLAY[layer.unit]
        lut = _lut(layer.colors)
        inv = self._inverse_display(layer)
        raw = [inv(back(v)) for v in legend]
        lo, hi = min(raw), max(raw)
        def colour(rv: float) -> str:
            k = int(np.clip(round((rv - layer.vmin) / (layer.vmax - layer.vmin) * 2048), 0, 2048))
            return hexc(lut[k])
        return {
            "type": "gradient",
            "unit": unit,
            "stops": [colour(lo + (hi - lo) * i / 15) for i in range(16)],
            "ticks": [[round((rv - lo) / (hi - lo or 1), 4), f"{dv:g}"] for dv, rv in zip(legend, raw)],
        }

    @staticmethod
    def _inverse_display(layer: MapLayer) -> Callable[[float], float]:
        # all display conversions are affine: derive inverse numerically
        a = layer.display(0.0)
        b = layer.display(1.0) - a
        return lambda d: (d - a) / b if b else d


# --------------------------------------------------------------------------
# Animation
# --------------------------------------------------------------------------

#: per layer: ("hours", step) = forecast frames, ("minutes_back", step) = past frames
ANIMATION = {
    "temperature": ("hours", 1), "precipitation": ("hours", 1), "wind": ("hours", 1),
    "clouds": ("hours", 1), "humidity": ("hours", 1), "visibility": ("hours", 1),
    "pressure": ("hours", 1), "dew_point": ("hours", 1), "air_quality": ("hours", 1),
    "winter": ("hours", 3), "satellite": ("minutes_back", 10),
    "tropical_cyclones": ("storm", 0),
    "radar": ("nowcast", 12),  # minutes between frames (data comes in 4 minute steps)
}


def encode_animation(frames: list[bytes], duration_ms: int = 700) -> bytes:
    """Combine PNG frames into an animated WebP (last frame shown longer)."""
    images = [Image.open(io.BytesIO(f)).convert("RGB") for f in frames]
    buf = io.BytesIO()
    durations = [duration_ms] * (len(images) - 1) + [duration_ms * 3]
    images[0].save(
        buf, format="WEBP", save_all=True, append_images=images[1:], duration=durations,
        loop=0, quality=78, method=3,
    )
    return buf.getvalue()
