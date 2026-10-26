"""Client and parser for the MSN weather overview API.

This module intentionally has no Home Assistant imports so it can be tested
standalone.
"""

from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass, field
import asyncio
from datetime import datetime, timedelta, timezone
import math
from typing import Any
from urllib.parse import parse_qs, urlparse

import aiohttp

from .const import (
    API_URL,
    APP_ID,
    HURRICANE_DETAIL_URL,
    HURRICANE_LIST_URL,
    LIFE_SUBTYPES,
    WEATHERTRENDS_URL,
)

LIFE_SUBTYPE_PARAM = ",".join(str(k) for k in LIFE_SUBTYPES)

_PAST_OR_FUTURE = re.compile(r"(PastDay|MultidayYesterday|FutureDay|Upcoming)$")

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0 Safari/537.36"
)


class MsnWeatherError(Exception):
    """Generic API error."""


class MsnWeatherAuthError(MsnWeatherError):
    """API key rejected."""


MSN_WEATHER_PAGE = "https://www.msn.com/en-us/weather/forecast"
# the msn.com weather page embeds its public web API key, e.g. "...&apiKey=j5i4g..."
_API_KEY_RE = re.compile(r"apiKey=([A-Za-z0-9]{30,64})")


def extract_api_key(html: str) -> str | None:
    """Most frequent apiKey=... value in the msn.com weather page."""
    keys = _API_KEY_RE.findall(html or "")
    return max(set(keys), key=keys.count) if keys else None


async def async_discover_api_key(session: aiohttp.ClientSession) -> str | None:
    """Fetch the current public API key from msn.com (MSN rotates it now and then)."""
    try:
        async with session.get(
            MSN_WEATHER_PAGE,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html"},
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            if resp.status != 200:
                return None
            return extract_api_key(await resp.text())
    except (aiohttp.ClientError, TimeoutError):
        return None


def parse_msn_url(url: str) -> tuple[float, float, str | None] | None:
    """Extract latitude, longitude and place name from an msn.com weather URL."""
    try:
        query = parse_qs(urlparse(url.strip()).query)
        loc = query.get("loc", [None])[0]
        if not loc:
            return None
        loc += "=" * (-len(loc) % 4)
        data = json.loads(base64.b64decode(loc).decode("utf-8"))
        return float(data["y"]), float(data["x"]), data.get("l")
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def parse_dt(value: Any) -> datetime | None:
    """Parse an ISO timestamp as returned by MSN."""
    if not value or not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


@dataclass
class MsnWeatherData:
    """Parsed weather data."""

    raw: dict[str, Any]
    location: dict[str, Any]
    provider: str | None
    current: dict[str, Any]
    days: list[dict[str, Any]]
    alerts: list[dict[str, Any]]
    nowcast: dict[str, Any]
    pollen: list[dict[str, Any]]
    pollen_provider: str | None
    life_today: dict[str, dict[str, Any]]
    life_tomorrow: dict[str, dict[str, Any]]
    insights: dict[str, dict[str, Any]] = field(default_factory=dict)
    fetched: datetime | None = None
    imperial: bool = False
    storms: list[dict[str, Any]] = field(default_factory=list)
    # storms after the user's radius / disturbance filter, ordered by map priority
    storms_visible: list[dict[str, Any]] = field(default_factory=list)
    day_details: dict[str, dict[str, Any]] = field(default_factory=dict)
    today_series: dict[str, dict[str, float]] = field(default_factory=dict)
    aqi_forecast: list[dict[str, Any]] = field(default_factory=list)
    climate: dict[str, Any] = field(default_factory=dict)
    monthly: list[dict[str, Any]] = field(default_factory=list)

    def day(self, offset: int) -> dict[str, Any]:
        """Details for today + offset days (offset -1 = yesterday)."""
        if not self.days:
            return {}
        start = parse_dt(self.days[0]["daily"].get("valid"))
        if not start:
            return {}
        key = (start + timedelta(days=offset)).strftime("%Y-%m-%d")
        return self.day_details.get(key, {})

    @property
    def today(self) -> dict[str, Any]:
        return self.days[0]["daily"] if self.days else {}

    @property
    def almanac(self) -> dict[str, Any]:
        return self.days[0].get("almanac", {}) if self.days else {}

    @property
    def hourly(self) -> list[dict[str, Any]]:
        return [h for d in self.days for h in d.get("hourly", [])]

    def insight(self, category: str) -> dict[str, Any]:
        return self.insights.get(category, {})

    @property
    def aqi_params(self) -> dict[str, Any]:
        return self.insight("AQI").get("parameters", {})

    @property
    def pollen_today(self) -> dict[str, Any]:
        return self.pollen[0] if self.pollen else {}


def _pick_insights(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Pick the insight describing *today* for every category."""
    result: dict[str, dict[str, Any]] = {}
    fallback: dict[str, dict[str, Any]] = {}
    for item in items:
        cat = item.get("category")
        if not cat:
            continue
        if not _PAST_OR_FUTURE.search(item.get("type", "")):
            result.setdefault(cat, item)
        elif item.get("type", "").endswith("FutureDay"):
            fallback.setdefault(cat, item)
    for cat, item in fallback.items():
        result.setdefault(cat, item)
    return result


_TICKS_EPOCH = 621355968000000000  # .NET ticks at 1970-01-01


def ticks_to_dt(ticks: Any) -> datetime | None:
    """Convert .NET ticks (UTC) to an aware datetime."""
    try:
        ticks = int(ticks)
    except (TypeError, ValueError):
        return None
    if ticks <= _TICKS_EPOCH:
        return None
    return datetime.fromtimestamp((ticks - _TICKS_EPOCH) / 1e7, tz=timezone.utc)


# insight category -> {parameter: field name in day details}
_DAY_FIELDS: dict[str, dict[str, str]] = {
    "Temperature": {"dailyHigh": "temp_high", "nightlyLow": "temp_low"},
    "FeelsLike": {"dailyHigh": "feels_high", "nightlyLow": "feels_low"},
    "Wind": {
        "dailyHigh": "wind_high", "dailyLow": "wind_low", "dailyGust": "wind_gust",
        "windSpeed": "wind_day", "windSpeedNight": "wind_night",
        "directionInFloat": "wind_dir_day", "directionNightInFloat": "wind_dir_night",
    },
    "Humidity": {"dailyHigh": "humidity_high", "dailyLow": "humidity_low"},
    "Precipitation": {
        "dayRainTotal": "rain_day", "nightRainTotal": "rain_night",
        "daySnowTotal": "snow_day", "nightSnowTotal": "snow_night",
    },
    "CloudCover": {"cloudCoverDay": "cloud_day", "cloudCoverNight": "cloud_night", "MaxCoverage": "cloud_max"},
    "Visibility": {
        "peakVisibility": "visibility_high", "lowVisibility": "visibility_low",
        "maxVisibility": "visibility_high", "minVisibility": "visibility_low",
    },
    "Pressure": {"dailyHigh": "pressure_high", "dailyLow": "pressure_low"},
    "UV": {"maxUvIndex": "uv_max"},
    "Pollen": {"pollenIndex": "pollen_index"},
}


def _day_details(items: list[dict[str, Any]], days: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Per-day values (yesterday … +9) collected from the MSN insights."""
    out: dict[str, dict[str, Any]] = {}
    for item in items:
        meta = item.get("metadata") or {}
        valid = str(meta.get("validDateTime") or "")
        if len(valid) < 10:
            continue
        key = valid[:10].replace("/", "-")
        day = out.setdefault(key, {"date": key, "texts": {}})
        cat = item.get("category") or ""
        params = item.get("parameters") or {}
        for src, dst in _DAY_FIELDS.get(cat, {}).items():
            val = params.get(src)
            if isinstance(val, (int, float)) and dst not in day:
                day[dst] = round(float(val), 2)
        if cat == "Pollen" and meta.get("mainAllergy"):
            day.setdefault("pollen_main", meta.get("mainAllergy"))
        text = item.get("fullText") or item.get("teaserText")
        if text and cat not in day["texts"]:
            day["texts"][cat] = text
        if meta.get("NightSummary") and cat + "_night" not in day["texts"]:
            day["texts"][cat + "_night"] = meta["NightSummary"]
    for day in out.values():
        rain = [day.get(k) for k in ("rain_day", "rain_night", "snow_day", "snow_night")]
        if any(v is not None for v in rain):
            day["precip_total"] = round(sum(v or 0 for v in rain), 2)
    # complete with forecast values
    for fday in days:
        d = fday.get("daily") or {}
        start = parse_dt(d.get("valid"))
        if not start:
            continue
        day = out.setdefault(start.strftime("%Y-%m-%d"), {"date": start.strftime("%Y-%m-%d"), "texts": {}})
        for src, dst in (
            ("tempHi", "temp_high"), ("tempLo", "temp_low"), ("feelsHi", "feels_high"),
            ("feelsLo", "feels_low"), ("rhHi", "humidity_high"), ("rhLo", "humidity_low"),
            ("uv", "uv_max"), ("aqi", "aqi"), ("precip", "precip_probability"),
            ("vis", "visibility"), ("baro", "pressure"), ("dewPt", "dew_point"),
        ):
            if isinstance(d.get(src), (int, float)):
                day.setdefault(dst, d[src])
        day.setdefault("symbol", d.get("symbol"))
        day.setdefault("condition_text", d.get("pvdrCap"))
        alm = fday.get("almanac") or {}
        for k in ("sunrise", "sunset", "moonrise", "moonset", "moonPhase"):
            if alm.get(k):
                day.setdefault(k.lower(), alm[k])
    return dict(sorted(out.items()))


def _today_series(items: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """Hourly curve of today for each category (used by the tile sparklines)."""
    out: dict[str, dict[str, float]] = {}
    for item in items:
        if _PAST_OR_FUTURE.search(item.get("type", "")):
            continue
        ts = item.get("timeSeries") or {}
        series = ts.get("trend") or next(
            (v for k, v in ts.items() if isinstance(v, dict) and len(v) > 6), None
        )
        cat = item.get("category")
        if cat and isinstance(series, dict) and cat not in out:
            out[cat] = {
                k: v for k, v in series.items() if isinstance(v, (int, float))
            }
    return out


def _aqi_forecast(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Hourly pollutant values (today + coming days) from the AQI insights."""
    rows: dict[str, dict[str, Any]] = {}
    for item in items:
        if item.get("category") != "AQI":
            continue
        for name, series in (item.get("timeSeries") or {}).items():
            if not isinstance(series, dict):
                continue
            key = {"trend": "aqi", "primaryPollutant": "primary_pollutant"}.get(name, name.lower())
            for ts, val in series.items():
                rows.setdefault(ts, {"time": ts})[key] = val
    return [rows[k] for k in sorted(rows)]


def _life(day: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not day:
        return {}
    out: dict[str, dict[str, Any]] = {}
    for idx in day.get("lifeDailyIndices", []):
        key = LIFE_SUBTYPES.get(idx.get("subType"))
        if key:
            item = dict(idx)
            item["hourly"] = [
                {
                    "time": t.isoformat(),
                    "category": h.get("categoryId"),
                    "value": h.get("value"),
                }
                for h in idx.get("hourlyIndices") or []
                if (t := ticks_to_dt(h.get("validTime")))
            ]
            out[key] = item
    return out


def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def storm_track(storm: dict[str, Any]) -> list[dict[str, Any]]:
    """Observed + forecast positions of a storm, oldest first."""
    track = []
    for f in storm.get("features") or []:
        g, pr = f.get("geometry") or {}, f.get("properties") or {}
        if g.get("type") != "Point" or not g.get("coordinates"):
            continue
        t = parse_dt(pr.get("datetime"))
        if t is None:
            continue
        track.append({
            "time": t,
            "lon": g["coordinates"][0],
            "lat": g["coordinates"][1],
            "category": pr.get("category") or "",
            "max_wind": pr.get("maxWind"),
            "max_gust": pr.get("maxGust"),
            "forecast": pr.get("dataType") == "Forecast",
        })
    track.sort(key=lambda p: p["time"])
    return track


def parse_storms(
    listing: dict[str, Any], details: dict[str, list], lat: float, lon: float
) -> list[dict[str, Any]]:
    """Active tropical cyclones (incl. disturbances) sorted by distance."""
    storms = []
    for feat in listing.get("features") or []:
        props = feat.get("properties") or {}
        latest = props.get("latestProperties") or {}
        s_lat, s_lon = latest.get("lat"), latest.get("lng")
        category = latest.get("category") or props.get("category") or ""
        storm = {
            "id": feat.get("id"),
            "name": props.get("name"),
            "local_name": props.get("localName"),
            "category": category,
            "disturbance": category.startswith("OL"),
            "max_wind": latest.get("maxWind"),
            "max_gust": latest.get("maxGust"),
            "pressure": latest.get("pressure"),
            "movement": latest.get("movement"),
            "latitude": s_lat,
            "longitude": s_lon,
            "peak_category": props.get("category"),
            "peak_wind": props.get("maxWind"),
            "min_pressure": props.get("minPressure"),
            "start": props.get("startDate"),
            "end": props.get("endDate"),
            "time": latest.get("time"),
            "distance_km": round(_distance_km(lat, lon, s_lat, s_lon))
            if isinstance(s_lat, (int, float)) and isinstance(s_lon, (int, float))
            else None,
            "features": details.get(feat.get("id"), []),
        }
        storm["track"] = storm_track(storm)
        # the list reports wind in mph; the track points carry km/h
        current = [p for p in storm["track"] if not p["forecast"]]
        if current and current[-1]["max_wind"] is not None:
            storm["max_wind"] = current[-1]["max_wind"]
            storm["max_gust"] = current[-1]["max_gust"]
        # closest approach: current position or any forecast position
        dists = [storm["distance_km"]] if storm["distance_km"] is not None else []
        dists += [
            _distance_km(lat, lon, p["lat"], p["lon"]) for p in storm["track"] if p["forecast"]
        ]
        storm["closest_km"] = round(min(dists)) if dists else None
        storms.append(storm)
    storms.sort(key=lambda s: (s["disturbance"], s["distance_km"] or 1e9))
    return storms


def parse_response(payload: dict[str, Any]) -> MsnWeatherData:
    """Turn the raw API payload into MsnWeatherData."""
    try:
        resp = payload["responses"][0]
        weather = resp["weather"][0]
    except (KeyError, IndexError, TypeError) as err:
        raise MsnWeatherError(f"Unexpected response: {err}") from err

    source = resp.get("source", {})
    life_days = (weather.get("LifeActivityResp") or {}).get("days") or []
    pollen = weather.get("pollen") or {}

    return MsnWeatherData(
        raw=weather,
        location={
            "id": source.get("id"),
            "name": (source.get("location") or {}).get("Name"),
            "timezone": (source.get("location") or {}).get("TimezoneName"),
            **(source.get("coordinates") or {}),
        },
        provider=(weather.get("provider") or {}).get("name"),
        current=weather.get("current") or {},
        days=(weather.get("forecast") or {}).get("days") or [],
        alerts=weather.get("alerts") or [],
        nowcast=weather.get("nowcasting") or {},
        pollen=pollen.get("forecast") or [],
        pollen_provider=(pollen.get("provider") or {}).get("name"),
        life_today=_life(life_days[0] if life_days else None),
        life_tomorrow=_life(life_days[1] if len(life_days) > 1 else None),
        insights=_pick_insights((weather.get("insights") or {}).get("insights") or []),
        day_details=_day_details(
            (weather.get("insights") or {}).get("insights") or [],
            (weather.get("forecast") or {}).get("days") or [],
        ),
        today_series=_today_series((weather.get("insights") or {}).get("insights") or []),
        aqi_forecast=_aqi_forecast((weather.get("insights") or {}).get("insights") or []),
    )


class MsnWeatherClient:
    """Small async client for the MSN weather overview endpoint."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        latitude: float,
        longitude: float,
        language: str,
        api_key: str,
        imperial: bool = False,
    ) -> None:
        self._session = session
        # MSN returns values *and* texts in °F / mph / inHg / mi / in with units=F
        self.units = "F" if imperial else "C"
        self.latitude = latitude
        self.longitude = longitude
        self.language = language
        self.api_key = api_key

    def _params(self) -> dict[str, str]:
        return {
            "apikey": self.api_key,
            "appId": APP_ID,
            "ocid": "msftweather",
            "cm": self.language,
            "market": self.language,
            "locale": self.language,
            "region": self.language.split("-")[-1],
            "it": "web",
            "scn": "ANON",
            "units": self.units,
            "wrapodata": "false",
            "cuthour": "true",
            "days": "10",
            "includestorm": "true",
            "includeLifeActivity": "true",
            "lifeDays": "2",
            "lifeModes": "17",
            "lifeSubTypes": LIFE_SUBTYPE_PARAM,
            "insights": "65536",
            "startDate": "-1",
            "endDate": "+9",
            "distanceinkm": "0",
            "regionDataCount": "20",
            "orderby": "distance",
            "source": "weather_csr",
            "lat": f"{self.latitude:.6f}",
            "lon": f"{self.longitude:.6f}",
        }

    async def async_get_raw(self) -> dict[str, Any]:
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Origin": "https://www.msn.com",
            "Referer": "https://www.msn.com/",
        }
        try:
            async with self._session.get(
                API_URL,
                params=self._params(),
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status in (401, 403):
                    raise MsnWeatherAuthError(f"HTTP {resp.status}")
                if resp.status != 200:
                    raise MsnWeatherError(f"HTTP {resp.status}")
                return await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise MsnWeatherError(str(err)) from err

    async def async_get(self) -> MsnWeatherData:
        return parse_response(await self.async_get_raw())

    async def _get_json(self, url: str, params: dict[str, str]) -> dict[str, Any]:
        try:
            async with self._session.get(
                url,
                params=params,
                headers={"User-Agent": USER_AGENT, "Referer": "https://www.msn.com/"},
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status != 200:
                    raise MsnWeatherError(f"HTTP {resp.status}")
                return await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise MsnWeatherError(str(err)) from err

    async def async_get_climate(self) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Climate normals/records for today and the ~30 day calendar forecast."""
        today = datetime.now()
        common = {
            "apiKey": self.api_key,
            "cm": self.language,
            "locale": self.language,
            "lat": f"{self.latitude:.6f}",
            "lon": f"{self.longitude:.6f}",
            "units": self.units,
            "ocid": "msftweather",
            "days": "30",
        }
        trends, calendar = await asyncio.gather(
            self._get_json(
                WEATHERTRENDS_URL,
                {
                    **common,
                    "includeWeatherTrends": "true",
                    "includeCalendar": "false",
                    "weatherTrendsScenarios": "TemperatureTrend,OverviewSummary,Summary,ClimateSummary",
                    "insights": "1",
                    "startDate": (today.replace(day=1) - timedelta(days=300)).strftime("%Y%m01"),
                    "endDate": today.strftime("%Y%m%d"),
                },
            ),
            self._get_json(
                WEATHERTRENDS_URL,
                {
                    **common,
                    "includeWeatherTrends": "false",
                    "includeCalendar": "true",
                    "weatherTrendsScenarios": "Calendar",
                    "startDate": today.strftime("%Y%m%d"),
                    "endDate": (today + timedelta(days=40)).strftime("%Y%m%d"),
                    "calendarStartDate": today.strftime("%Y%m%d"),
                    "calendarEndDate": (today + timedelta(days=40)).strftime("%Y%m%d"),
                },
            ),
            return_exceptions=True,
        )
        climate = parse_climate(trends) if isinstance(trends, dict) else {}
        monthly = parse_calendar(calendar) if isinstance(calendar, dict) else []
        return climate, monthly

    async def async_get_storms(self) -> list[dict[str, Any]]:
        """Active tropical cyclones worldwide (NHC / JMA / CMA via MSN)."""
        common = {
            "wrapOData": "false",
            "ids": "",
            "units": "C",
            "mkt": "en-us,ja-jp",
            "locale": self.language,
            "apiKey": self.api_key,
            "ocid": "msftweather",
        }
        listing = await self._get_json(
            HURRICANE_LIST_URL, {**common, "hurricanelisttype": "ActiveList"}
        )
        ids = [f.get("id") for f in listing.get("features") or [] if f.get("id")]

        async def detail(storm_id: str) -> tuple[str, list]:
            try:
                data = await self._get_json(
                    HURRICANE_DETAIL_URL, {**common, "hurricaneid": storm_id}
                )
            except MsnWeatherError:
                return storm_id, []
            return storm_id, data.get("features") or []

        details = dict(await asyncio.gather(*(detail(i) for i in ids)))
        return parse_storms(listing, details, self.latitude, self.longitude)


# MSN enum "HistoricalSummaryData"
_HIST = {
    1: "avg_rain", 2: "avg_snow", 3: "avg_humidity", 4: "avg_wind", 5: "avg_high", 6: "avg_low",
    7: "record_rain", 8: "record_snow", 9: "record_humidity", 10: "record_wind",
    11: "record_high", 12: "record_low", 13: "record_rain_year", 14: "record_snow_year",
    15: "record_humidity_year", 16: "record_wind_year", 17: "record_high_year",
    18: "record_low_year", 19: "rainy_years", 20: "snowy_years",
}
# MSN enum "OverviewSummary" (current month vs. climate)
_OVERVIEW = {
    1: "snow_days", 2: "historical_snow_days", 3: "rainy_days", 4: "historical_rainy_days",
    5: "sunny_days", 6: "historical_sunny_days", 7: "cloudy_days", 8: "historical_cloudy_days",
    9: "avg_high", 10: "historical_avg_high", 11: "avg_low", 12: "historical_avg_low",
}


def _hist_day(entry: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for src in (entry.get("historicalSummaryData") or {}, entry.get("historicalSummaryDays") or {}):
        for k, v in src.items():
            name = _HIST.get(int(k)) if str(k).isdigit() else None
            if not name:
                continue
            if name.endswith("_year") and isinstance(v, str):
                v = int(v[:4])
            out[name] = v
    return out


def parse_climate(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        resp = payload["value"][0]["responses"][0]
    except (KeyError, IndexError, TypeError):
        return {}
    days = {
        k[:10]: _hist_day(v) for k, v in (resp.get("historicalSummaryDays") or {}).items()
    }
    overview = {
        _OVERVIEW[int(k)]: v
        for k, v in (resp.get("overviewSummary") or {}).items()
        if str(k).isdigit() and int(k) in _OVERVIEW
    }
    return {
        "days": days,
        "month": overview,
        "since": (resp.get("historicalDataStartYear") or "")[:4],
    }


def parse_calendar(payload: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        days = payload["value"][0]["responses"][0]["calendar"]["weather"][0]["days"]
    except (KeyError, IndexError, TypeError):
        return []
    out = []
    for item in days:
        d = item.get("daily") or {}
        valid = str(d.get("valid") or "")[:10]
        if not valid:
            continue
        out.append(
            {
                "date": valid,
                "condition": condition_from_symbol(d.get("symbol")),
                "temp_high": d.get("tempHi"),
                "temp_low": d.get("tempLo"),
                "precipitation_probability": d.get("precip"),
                "wind_max": d.get("windMax"),
                "wind_dir": d.get("windMaxDir"),
                "humidity_high": d.get("rhHi"),
            }
        )
    return out


def condition_from_symbol(symbol: str | None, wx: str | None = None) -> str | None:
    """Map an MSN/Foreca symbol code (e.g. 'd4100') to a HA condition.

    Code layout: [d|n][clouds 0-4][precip intensity 0-3][type 0 rain/1 sleet/2 snow][thunder 0/1]
    """
    if not symbol or len(symbol) < 2:
        return None
    is_day = symbol[0] != "n"
    digits = (symbol[1:] + "0000")[:4]
    try:
        clouds, intensity, ptype, thunder = (int(c) for c in digits)
    except ValueError:
        return None
    wx = (wx or "").upper()

    if thunder or "TS" in wx:
        return "lightning-rainy" if intensity else "lightning"
    if "GR" in wx or "GS" in wx:
        return "hail"
    if intensity:
        if ptype == 2:
            return "snowy"
        if ptype == 1:
            return "snowy-rainy"
        return "pouring" if intensity >= 3 else "rainy"
    if "FG" in wx:
        return "fog"
    if clouds == 0:
        return "sunny" if is_day else "clear-night"
    if clouds <= 2:
        return "partlycloudy"
    return "cloudy"


_COMPASS = {
    "de": ["N", "NNO", "NO", "ONO", "O", "OSO", "SO", "SSO", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"],
    "it": ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO"],
    "en": ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"],
    "fr": ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO"],
    "es": ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO"],
    "nl": ["N", "NNO", "NO", "ONO", "O", "OZO", "ZO", "ZZO", "Z", "ZZW", "ZW", "WZW", "W", "WNW", "NW", "NNW"],
}


def compass(bearing: float | None, language: str) -> str | None:
    if bearing is None:
        return None
    names = _COMPASS.get(language[:2], _COMPASS["en"])
    return names[int((bearing % 360) / 22.5 + 0.5) % 16]
