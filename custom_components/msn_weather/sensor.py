"""Sensors for MSN Weather – mirrors the "weather details" tiles and the life indices."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import math
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    DEGREE,
    PERCENTAGE,
    UV_INDEX,
    EntityCategory,
    UnitOfLength,
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant

try:  # HA >= 2026.x
    from homeassistant.const import UnitOfDensity, UnitOfRatio

    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER = UnitOfDensity.MICROGRAMS_PER_CUBIC_METER
    CONCENTRATION_PARTS_PER_BILLION = UnitOfRatio.PARTS_PER_BILLION
except ImportError:  # older HA
    from homeassistant.const import (
        CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        CONCENTRATION_PARTS_PER_BILLION,
    )
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .api import MsnWeatherData, compass, condition_from_symbol, parse_dt
from .const import LIFE_SUBTYPES
from .coordinator import MsnWeatherConfigEntry, MsnWeatherCoordinator
from .units import IMPERIAL_PRECISION, IMPERIAL_UNITS, kmh
from .entity import MsnWeatherEntity


def _insight_attrs(category: str) -> Callable[[MsnWeatherData], dict[str, Any]]:
    """Attributes with the texts shown on the MSN card (headline, summary, trend)."""

    def fn(data: MsnWeatherData) -> dict[str, Any]:
        ins = data.insight(category)
        if not ins:
            return {}
        return {
            "headline": ins.get("headlineText") or None,
            "summary": ins.get("teaserText") or None,
            "details": ins.get("fullText") or None,
            "trend": ins.get("trend"),
        }

    return fn


def _series(category: str) -> Callable[[MsnWeatherData], dict[str, Any]]:
    return lambda d: {"today_series": d.today_series.get(category)} if d.today_series.get(category) else {}


def _yday(key: str) -> Callable[[MsnWeatherData], Any]:
    return lambda d: d.day(-1).get(key)


def _clim(key: str) -> Callable[[MsnWeatherData], Any]:
    def fn(d: MsnWeatherData) -> Any:
        today = d.day(0).get("date") or ""
        return ((d.climate.get("days") or {}).get(today) or {}).get(key)

    return fn


def _merge(*fns: Callable[[MsnWeatherData], dict[str, Any]]):
    def fn(data: MsnWeatherData) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for f in fns:
            out.update(f(data))
        return out

    return fn


def _daylight_minutes(data: MsnWeatherData) -> float | None:
    rise, sset = parse_dt(data.almanac.get("sunrise")), parse_dt(data.almanac.get("sunset"))
    if rise and sset:
        return round((sset - rise).total_seconds() / 60)
    return None


def _moon_minutes(data: MsnWeatherData) -> float | None:
    rise, mset = parse_dt(data.almanac.get("moonrise")), parse_dt(data.almanac.get("moonset"))
    if rise and mset:
        delta = (mset - rise).total_seconds()
        if delta < 0:
            delta += 86400
        return round(delta / 60)
    return None


_REF_NEW_MOON = datetime(2000, 1, 6, 18, 14, tzinfo=UTC)
_SYNODIC_DAYS = 29.530588853


def _next_full_moon() -> datetime:
    """Approximate next full moon (mean lunation, accurate to about a day)."""
    days = (dt_util.utcnow() - _REF_NEW_MOON).total_seconds() / 86400
    lunation = math.ceil((days - _SYNODIC_DAYS / 2) / _SYNODIC_DAYS)
    full = _REF_NEW_MOON + timedelta(days=lunation * _SYNODIC_DAYS + _SYNODIC_DAYS / 2)
    return dt_util.as_local(full)


def _pollen_attrs(data: MsnWeatherData) -> dict[str, Any]:
    today = data.pollen_today
    attrs: dict[str, Any] = {
        "level": today.get("levelName"),
        "main_allergen": today.get("typeName"),
        "provider": data.pollen_provider,
    }
    for sub in today.get("subTypes", []):
        attrs[sub.get("typeName")] = sub.get("pollenindex")
    attrs["forecast"] = [
        {
            "date": p.get("valid"),
            "index": p.get("pollenindex"),
            "level": p.get("levelName"),
            "main_allergen": p.get("typeName"),
        }
        for p in data.pollen
    ]
    return attrs


def _alert_list(data: MsnWeatherData) -> list[dict[str, Any]]:
    return [
        {
            "title": a.get("title"),
            "event": a.get("event"),
            "level": a.get("level"),
            # NWS style significance: W warning, A watch, Y advisory, S statement
            "significance": a.get("significance"),
            "severity": a.get("severity"),
            "status": a.get("statusText"),
            "start": a.get("start"),
            "end": a.get("end"),
            "description": a.get("shortCap"),
            "safety_guide": a.get("safetyGuide"),
            "source": a.get("credit"),
        }
        for a in data.alerts
    ]


def _nowcast_attrs(data: MsnWeatherData) -> dict[str, Any]:
    n = data.nowcast
    return {
        "short_summary": n.get("shortSummary"),
        "taskbar_summary": n.get("taskbarSummary"),
        # NoRain, RainStarting, RainStopping, Raining, … and the minutes until that change
        "template_type": n.get("templateType"),
        "minutes_to_change": n.get("minutesToTransit"),
        "precipitation_type": n.get("raintype"),
        "minutes_between_values": n.get("minutesBetweenHorrizons"),
        "previous_precipitation": n.get("previousPrecipitation"),
        "precipitation": n.get("precipitation"),
        "precipitation_rate": n.get("precipitationRate"),
        "precipitation_accumulation": n.get("precipitationAccumulation"),
        "nearest_precipitation_km": n.get("nowcastingDistance"),
        "timestamp": n.get("timestamp"),
    }


STORM_CATEGORIES = {
    "TD": "Tropical depression",
    "TS": "Tropical storm",
    "STS": "Severe tropical storm",
    "TY": "Typhoon",
    "STY": "Super typhoon",
    "H1": "Hurricane cat. 1",
    "H2": "Hurricane cat. 2",
    "H3": "Hurricane cat. 3",
    "H4": "Hurricane cat. 4",
    "H5": "Hurricane cat. 5",
}


def _storm_summary(storm: dict[str, Any] | None, imperial: bool = False) -> dict[str, Any] | None:
    if not storm:
        return None
    cat = storm.get("category") or ""
    return {
        "name": storm.get("name"),
        "category": cat,
        "category_text": "Disturbance" if cat.startswith("OL") else STORM_CATEGORIES.get(cat, cat),
        "max_wind": kmh(storm.get("max_wind"), imperial),
        "max_gust": kmh(storm.get("max_gust"), imperial),
        "wind_unit": "mph" if imperial else "km/h",
        "pressure": storm.get("pressure"),
        "movement": storm.get("movement"),
        "latitude": storm.get("latitude"),
        "longitude": storm.get("longitude"),
        "distance_km": storm.get("distance_km"),
        "closest_km": storm.get("closest_km"),
        "peak_category": storm.get("peak_category"),
        "start": storm.get("start"),
    }


@dataclass(frozen=True, kw_only=True)
class MsnSensorDescription(SensorEntityDescription):
    value_fn: Callable[[MsnWeatherData], Any]
    attr_fn: Callable[[MsnWeatherData], dict[str, Any]] | None = None


def _cur(key: str) -> Callable[[MsnWeatherData], Any]:
    return lambda d: d.current.get(key)


def _today(key: str) -> Callable[[MsnWeatherData], Any]:
    return lambda d: d.today.get(key)


def _aqi(key: str) -> Callable[[MsnWeatherData], Any]:
    return lambda d: d.aqi_params.get(key)


MEASUREMENT = SensorStateClass.MEASUREMENT
# MEASUREMENT_ANGLE only exists in newer HA versions
MEASUREMENT_ANGLE = getattr(SensorStateClass, "MEASUREMENT_ANGLE", None)

SENSORS: tuple[MsnSensorDescription, ...] = (
    # --- Temperature / feels like -------------------------------------------
    MsnSensorDescription(
        key="temperature",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=MEASUREMENT,
        value_fn=_cur("temp"),
        attr_fn=_merge(_insight_attrs("Temperature"), _series("Temperature")),
    ),
    MsnSensorDescription(
        key="temperature_high",
        translation_key="temperature_high",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=_today("tempHi"),
    ),
    MsnSensorDescription(
        key="temperature_low",
        translation_key="temperature_low",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=_today("tempLo"),
    ),
    MsnSensorDescription(
        key="apparent_temperature",
        translation_key="apparent_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=MEASUREMENT,
        value_fn=_cur("feels"),
        attr_fn=_merge(_series("FeelsLike"), 
            _insight_attrs("FeelsLike"),
            lambda d: {
                "today_high": d.today.get("feelsHi"),
                "today_low": d.today.get("feelsLo"),
            },
        ),
    ),
    MsnSensorDescription(
        key="dew_point",
        translation_key="dew_point",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=MEASUREMENT,
        value_fn=_cur("dewPt"),
    ),
    # --- Cloud cover -------------------------------------------------------
    MsnSensorDescription(
        key="condition",
        translation_key="condition",
        value_fn=_cur("cap"),
        attr_fn=lambda d: {
            "short": d.current.get("capAbbr"),
            "condition": condition_from_symbol(d.current.get("symbol"), d.current.get("wx")),
            "symbol": d.current.get("symbol"),
            "icon_url": d.current.get("urlIcon"),
            "day_summary": (d.today.get("day") or {}).get("summary"),
            "night_summary": (d.today.get("night") or {}).get("summary"),
        },
    ),
    MsnSensorDescription(
        key="cloud_cover",
        translation_key="cloud_cover",
        native_unit_of_measurement=PERCENTAGE,
        state_class=MEASUREMENT,
        value_fn=_cur("cloudCover"),
        attr_fn=_merge(_series("CloudCover"), 
            _insight_attrs("CloudCover"),
            lambda d: {
                "cloud_cover_day": d.insight("CloudCover").get("parameters", {}).get("cloudCoverDay"),
                "cloud_cover_night": d.insight("CloudCover").get("parameters", {}).get("cloudCoverNight"),
            },
        ),
    ),
    # --- Precipitation --------------------------------------------------
    MsnSensorDescription(
        key="precipitation_today",
        translation_key="precipitation_today",
        device_class=SensorDeviceClass.PRECIPITATION,
        native_unit_of_measurement=UnitOfPrecipitationDepth.MILLIMETERS,
        value_fn=lambda d: round((d.today.get("raToMN") or 0) + (d.today.get("saToMN") or 0), 2)
        if d.today
        else None,
        attr_fn=_merge(
            _insight_attrs("Precipitation"),
            lambda d: {"rain": d.today.get("raToMN"), "snow": d.today.get("saToMN")},
        ),
    ),
    MsnSensorDescription(
        key="precipitation_probability",
        translation_key="precipitation_probability",
        native_unit_of_measurement=PERCENTAGE,
        value_fn=_today("precip"),
        attr_fn=lambda d: {
            "day": (d.today.get("day") or {}).get("precip"),
            "night": (d.today.get("night") or {}).get("precip"),
            "next_hour": d.hourly[0].get("precip") if d.hourly else None,
        },
    ),
    MsnSensorDescription(
        key="nowcast",
        translation_key="nowcast",
        value_fn=lambda d: d.nowcast.get("summary"),
        attr_fn=_nowcast_attrs,
    ),
    MsnSensorDescription(
        # minutes until rain starts / stops (None when nothing changes in the next 2 h)
        key="nowcast_change",
        translation_key="nowcast_change",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        value_fn=lambda d: d.nowcast.get("minutesToTransit")
        if d.nowcast.get("templateType") not in (None, "NoRain", "MajorityIntensity")
        and d.nowcast.get("minutesToTransit")
        else None,
        attr_fn=lambda d: {
            "change": d.nowcast.get("templateType"),
            "summary": d.nowcast.get("shortSummary"),
        },
    ),
    # --- Wind ------------------------------------------------------------
    MsnSensorDescription(
        key="wind_speed",
        translation_key="wind_speed",
        device_class=SensorDeviceClass.WIND_SPEED,
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        state_class=MEASUREMENT,
        value_fn=_cur("windSpd"),
        attr_fn=_merge(_insight_attrs("Wind"), _series("Wind")),
    ),
    MsnSensorDescription(
        key="wind_gust",
        translation_key="wind_gust",
        device_class=SensorDeviceClass.WIND_SPEED,
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        state_class=MEASUREMENT,
        value_fn=_cur("windGust"),
    ),
    MsnSensorDescription(
        key="wind_bearing",
        translation_key="wind_bearing",
        native_unit_of_measurement=DEGREE,
        state_class=MEASUREMENT_ANGLE,
        value_fn=_cur("windDir"),
    ),
    # --- Luftfeuchtigkeit ------------------------------------------------
    MsnSensorDescription(
        key="humidity",
        translation_key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=MEASUREMENT,
        value_fn=_cur("rh"),
        attr_fn=_merge(_series("Humidity"), 
            _insight_attrs("Humidity"),
            lambda d: {"today_high": d.today.get("rhHi"), "today_low": d.today.get("rhLo")},
        ),
    ),
    # --- UV --------------------------------------------------------------
    MsnSensorDescription(
        key="uv_index",
        translation_key="uv_index",
        native_unit_of_measurement=UV_INDEX,
        state_class=MEASUREMENT,
        value_fn=_cur("uv"),
        attr_fn=_merge(_series("UV"), 
            _insight_attrs("UV"),
            lambda d: {
                "level": d.current.get("uvDesc"),
                "today_max": d.today.get("uv"),
                "today_max_level": d.today.get("uvDesc"),
            },
        ),
    ),
    # --- AQI -------------------------------------------------------------
    MsnSensorDescription(
        key="aqi",
        translation_key="aqi",
        device_class=SensorDeviceClass.AQI,
        state_class=MEASUREMENT,
        value_fn=_cur("aqi"),
        attr_fn=_merge(
            _insight_attrs("AQI"),
            lambda d: {
                "severity": d.current.get("aqiSeverity"),
                "primary_pollutant": d.current.get("primaryPollutant"),
                "today_max": d.today.get("aqi"),
                "valid": d.current.get("aqiValidTime"),
                "forecast": d.aqi_forecast,
            },
        ),
    ),
    MsnSensorDescription(
        key="ozone",
        translation_key="ozone",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_BILLION,
        state_class=MEASUREMENT,
        value_fn=_aqi("curO3"),
    ),
    MsnSensorDescription(
        key="pm25",
        translation_key="pm25",
        device_class=SensorDeviceClass.PM25,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=MEASUREMENT,
        value_fn=_aqi("curPM25"),
    ),
    MsnSensorDescription(
        key="pm10",
        translation_key="pm10",
        device_class=SensorDeviceClass.PM10,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=MEASUREMENT,
        value_fn=_aqi("curPM10"),
    ),
    MsnSensorDescription(
        key="no2",
        translation_key="no2",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_BILLION,
        state_class=MEASUREMENT,
        value_fn=_aqi("curNO2"),
    ),
    MsnSensorDescription(
        key="co",
        translation_key="co",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_BILLION,
        state_class=MEASUREMENT,
        value_fn=_aqi("curCO"),
    ),
    MsnSensorDescription(
        key="so2",
        translation_key="so2",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_BILLION,
        state_class=MEASUREMENT,
        value_fn=_aqi("curSO2"),
    ),
    # --- Pollen ----------------------------------------------------------
    MsnSensorDescription(
        key="pollen",
        translation_key="pollen",
        state_class=MEASUREMENT,
        value_fn=lambda d: d.pollen_today.get("pollenindex"),
        attr_fn=_merge(_insight_attrs("Pollen"), _pollen_attrs),
    ),
    # --- Sichtbarkeit ----------------------------------------------------
    MsnSensorDescription(
        key="visibility",
        translation_key="visibility",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        state_class=MEASUREMENT,
        value_fn=_cur("vis"),
        attr_fn=_merge(_series("Visibility"), 
            _insight_attrs("Visibility"),
            lambda d: {
                "level": d.insight("Visibility").get("metadata", {}).get("visibility"),
                "today_max": d.insight("Visibility").get("parameters", {}).get("maxVisibility"),
                "today_min": d.insight("Visibility").get("parameters", {}).get("minVisibility"),
            },
        ),
    ),
    # --- Druck -----------------------------------------------------------
    MsnSensorDescription(
        key="pressure",
        translation_key="pressure",
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        native_unit_of_measurement=UnitOfPressure.MBAR,
        state_class=MEASUREMENT,
        value_fn=_cur("baro"),
        attr_fn=_merge(_insight_attrs("Pressure"), _series("Pressure")),
    ),
    # --- Sonne -----------------------------------------------------------
    MsnSensorDescription(
        key="sunrise",
        translation_key="sunrise",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda d: parse_dt(d.almanac.get("sunrise")),
    ),
    MsnSensorDescription(
        key="sunset",
        translation_key="sunset",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda d: parse_dt(d.almanac.get("sunset")),
    ),
    MsnSensorDescription(
        key="daylight",
        translation_key="daylight",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        value_fn=_daylight_minutes,
    ),
    # --- Mond ------------------------------------------------------------
    MsnSensorDescription(
        key="moonrise",
        translation_key="moonrise",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda d: parse_dt(d.almanac.get("moonrise")),
    ),
    MsnSensorDescription(
        key="moonset",
        translation_key="moonset",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda d: parse_dt(d.almanac.get("moonset")),
    ),
    MsnSensorDescription(
        key="moon_visible",
        translation_key="moon_visible",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        value_fn=_moon_minutes,
    ),
    MsnSensorDescription(
        key="moon_phase",
        translation_key="moon_phase",
        value_fn=lambda d: d.almanac.get("moonPhase"),
        attr_fn=lambda d: {
            "code": d.almanac.get("moonPhaseCode"),
            "next_full_moon": _next_full_moon().date().isoformat(),
        },
    ),
    MsnSensorDescription(
        key="moon_illumination",
        translation_key="moon_illumination",
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda d: d.insight("MoonAlmanac").get("parameters", {}).get("moonPhasePercentage"),
    ),
    # --- Alerts ----------------------------------------------------------
    MsnSensorDescription(
        key="alerts",
        translation_key="alerts",
        state_class=MEASUREMENT,
        value_fn=lambda d: len(d.alerts),
        attr_fn=lambda d: {
            "alerts": _alert_list(d),
            **_insight_attrs("SevereWeather")(d),
        },
    ),
    # --- Yesterday ---------------------------------------------------------
    MsnSensorDescription(
        key="yesterday_temp_high", translation_key="yesterday_temp_high",
        device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=_yday("temp_high"),
        attr_fn=lambda d: {"summary": d.day(-1).get("texts", {}).get("Temperature"), "date": d.day(-1).get("date")},
    ),
    MsnSensorDescription(
        key="yesterday_temp_low", translation_key="yesterday_temp_low",
        device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=_yday("temp_low"),
    ),
    MsnSensorDescription(
        key="yesterday_precipitation", translation_key="yesterday_precipitation",
        device_class=SensorDeviceClass.PRECIPITATION, native_unit_of_measurement=UnitOfPrecipitationDepth.MILLIMETERS,
        value_fn=_yday("precip_total"),
        attr_fn=lambda d: {k: d.day(-1).get(k) for k in ("rain_day", "rain_night", "snow_day", "snow_night")},
    ),
    MsnSensorDescription(
        key="yesterday_feels_high", translation_key="yesterday_feels_high", entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=_yday("feels_high"),
    ),
    MsnSensorDescription(
        key="yesterday_feels_low", translation_key="yesterday_feels_low", entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=_yday("feels_low"),
    ),
    MsnSensorDescription(
        key="yesterday_wind_max", translation_key="yesterday_wind_max", entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.WIND_SPEED, native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        value_fn=_yday("wind_high"),
    ),
    MsnSensorDescription(
        key="yesterday_wind_gust", translation_key="yesterday_wind_gust", entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.WIND_SPEED, native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        value_fn=_yday("wind_gust"),
    ),
    MsnSensorDescription(
        key="yesterday_humidity_high", translation_key="yesterday_humidity_high", entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.HUMIDITY, native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda d: round(d.day(-1)["humidity_high"]) if d.day(-1).get("humidity_high") is not None else None,
    ),
    MsnSensorDescription(
        key="yesterday_humidity_low", translation_key="yesterday_humidity_low", entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.HUMIDITY, native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda d: round(d.day(-1)["humidity_low"]) if d.day(-1).get("humidity_low") is not None else None,
    ),
    MsnSensorDescription(
        key="yesterday_pressure_high", translation_key="yesterday_pressure_high", entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE, native_unit_of_measurement=UnitOfPressure.MBAR,
        value_fn=_yday("pressure_high"),
    ),
    MsnSensorDescription(
        key="yesterday_pressure_low", translation_key="yesterday_pressure_low", entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE, native_unit_of_measurement=UnitOfPressure.MBAR,
        value_fn=_yday("pressure_low"),
    ),
    MsnSensorDescription(
        key="yesterday_uv_max", translation_key="yesterday_uv_max", entity_registry_enabled_default=False,
        native_unit_of_measurement=UV_INDEX, value_fn=_yday("uv_max"),
    ),
    MsnSensorDescription(
        key="yesterday_visibility_max", translation_key="yesterday_visibility_max", entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.DISTANCE, native_unit_of_measurement=UnitOfLength.KILOMETERS,
        value_fn=_yday("visibility_high"),
    ),
    MsnSensorDescription(
        key="yesterday_cloud_cover", translation_key="yesterday_cloud_cover", entity_registry_enabled_default=False,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda d: round(d.day(-1)["cloud_day"]) if d.day(-1).get("cloud_day") is not None else None,
        attr_fn=lambda d: {"night": d.day(-1).get("cloud_night")},
    ),
    # --- Tagesdetails (gestern … +9) ------------------------------------------
    MsnSensorDescription(
        key="daily_details", translation_key="daily_details",
        value_fn=lambda d: len(d.day_details),
        attr_fn=lambda d: {"days": list(d.day_details.values())},
    ),
    # --- Klima (seit 1951) / Monatsvorhersage -----------------------------
    MsnSensorDescription(
        key="climate_avg_high", translation_key="climate_avg_high",
        device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=_clim("avg_high"),
        attr_fn=lambda d: {"since": d.climate.get("since"), "month": d.climate.get("month")},
    ),
    MsnSensorDescription(
        key="climate_avg_low", translation_key="climate_avg_low",
        device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=_clim("avg_low"),
    ),
    MsnSensorDescription(
        key="climate_record_high", translation_key="climate_record_high",
        device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=_clim("record_high"), attr_fn=lambda d: {"year": _clim("record_high_year")(d)},
    ),
    MsnSensorDescription(
        key="climate_record_low", translation_key="climate_record_low",
        device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=_clim("record_low"), attr_fn=lambda d: {"year": _clim("record_low_year")(d)},
    ),
    MsnSensorDescription(
        key="climate_avg_precipitation", translation_key="climate_avg_precipitation",
        device_class=SensorDeviceClass.PRECIPITATION, native_unit_of_measurement=UnitOfPrecipitationDepth.MILLIMETERS,
        value_fn=_clim("avg_rain"),
        attr_fn=lambda d: {
            "record": _clim("record_rain")(d), "record_year": _clim("record_rain_year")(d),
            "avg_snow": _clim("avg_snow")(d), "record_snow": _clim("record_snow")(d),
            "record_snow_year": _clim("record_snow_year")(d),
            "years_with_rain": _clim("rainy_years")(d), "years_with_snow": _clim("snowy_years")(d),
            "avg_humidity": _clim("avg_humidity")(d), "avg_wind": _clim("avg_wind")(d),
            "record_wind": _clim("record_wind")(d), "record_wind_year": _clim("record_wind_year")(d),
        },
    ),
    MsnSensorDescription(
        key="monthly_forecast", translation_key="monthly_forecast",
        value_fn=lambda d: len(d.monthly),
        attr_fn=lambda d: {"days": d.monthly},
    ),
    # --- Tropical cyclones -----------------------------------------
    MsnSensorDescription(
        key="tropical_cyclones",
        translation_key="tropical_cyclones",
        state_class=MEASUREMENT,
        # storms within the configured radius (worldwide when the radius is 0)
        value_fn=lambda d: sum(1 for s in d.storms_visible if not s["disturbance"]),
        attr_fn=lambda d: {
            "nearest": _storm_summary(min(
                (s for s in d.storms_visible if not s["disturbance"]),
                key=lambda s: s.get("distance_km") or 1e9, default=None,
            ), d.imperial),
            "strongest": _storm_summary(max(
                (s for s in d.storms_visible if not s["disturbance"]),
                key=lambda s: s.get("max_wind") or 0, default=None,
            ), d.imperial),
            "storms": [_storm_summary(s, d.imperial) for s in d.storms_visible],
            "worldwide": sum(1 for s in d.storms if not s["disturbance"]),
        },
    ),
    # --- Diagnose --------------------------------------------------------
    MsnSensorDescription(
        key="last_update",
        translation_key="last_update",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: parse_dt(d.current.get("created")),
        attr_fn=lambda d: {
            "provider": d.provider,
            "location": d.location,
            "fetched": d.fetched.isoformat() if d.fetched else None,
        },
    ),
)

# The activity indices are disabled by default to keep the entity list tidy.
_ACTIVITY_SUBTYPES = {"cycling", "gardening", "hiking", "running", "stargazing", "picnic"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MsnWeatherConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    entities: list[SensorEntity] = [MsnSensor(coordinator, desc) for desc in SENSORS]
    entities.append(MsnWindDirectionSensor(coordinator))
    data = coordinator.data
    entities.extend(
        MsnLifeSensor(coordinator, key)
        for key in LIFE_SUBTYPES.values()
        if key in data.life_today or key in data.life_tomorrow
    )
    async_add_entities(entities)


_UNRECORDED = frozenset(
    {
        "today_series", "forecast", "days", "hourly", "storms", "alerts", "month",
        "precipitation", "precipitation_rate", "precipitation_accumulation", "previous_precipitation", "details",
    }
)


class MsnSensor(MsnWeatherEntity, SensorEntity):
    entity_description: MsnSensorDescription
    _unrecorded_attributes = _UNRECORDED

    def __init__(self, coordinator: MsnWeatherCoordinator, description: MsnSensorDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description
        if coordinator.imperial and description.native_unit_of_measurement in IMPERIAL_UNITS:
            unit = IMPERIAL_UNITS[description.native_unit_of_measurement]
            self._attr_native_unit_of_measurement = unit
            if unit in IMPERIAL_PRECISION:
                self._attr_suggested_display_precision = IMPERIAL_PRECISION[unit]

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.attr_fn is None:
            return None
        return self.entity_description.attr_fn(self.coordinator.data)


class MsnWindDirectionSensor(MsnWeatherEntity, SensorEntity):
    _attr_translation_key = "wind_direction"

    def __init__(self, coordinator: MsnWeatherCoordinator) -> None:
        super().__init__(coordinator, "wind_direction")

    @property
    def native_value(self) -> str | None:
        return compass(self.coordinator.data.current.get("windDir"), self.coordinator.language)


class MsnLifeSensor(MsnWeatherEntity, SensorEntity):
    """One "health and safety" or "activities" life index."""

    _unrecorded_attributes = frozenset({"hourly"})

    def __init__(self, coordinator: MsnWeatherCoordinator, key: str) -> None:
        super().__init__(coordinator, f"life_{key}", object_key=key)
        self._key = key
        self._attr_translation_key = f"life_{key}"
        self._attr_entity_registry_enabled_default = key not in _ACTIVITY_SUBTYPES

    @property
    def available(self) -> bool:
        return super().available and self._key in self.coordinator.data.life_today

    @property
    def native_value(self) -> str | None:
        idx = self.coordinator.data.life_today.get(self._key)
        return idx.get("taskbarSummary") if idx else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        today = self.coordinator.data.life_today.get(self._key, {})
        tomorrow = self.coordinator.data.life_tomorrow.get(self._key, {})
        return {
            "summary": today.get("summary"),
            "category": today.get("category"),
            "value": today.get("value"),
            "tomorrow": tomorrow.get("taskbarSummary"),
            "tomorrow_summary": tomorrow.get("summary"),
            "tomorrow_category": tomorrow.get("category"),
            "hourly": today.get("hourly", []) + tomorrow.get("hourly", []),
        }
