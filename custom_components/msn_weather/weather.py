"""Weather entity for MSN Weather."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.weather import (
    Forecast,
    SingleCoordinatorWeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.const import (
    UnitOfLength,
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import condition_from_symbol, parse_dt
from .const import ATTRIBUTION
from .coordinator import MsnWeatherConfigEntry, MsnWeatherCoordinator
from .entity import device_info, suggested_entity_id


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MsnWeatherConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([MsnWeather(entry.runtime_data)])


def _sum(*values: Any) -> float | None:
    nums = [v for v in values if isinstance(v, (int, float))]
    return round(sum(nums), 2) if nums else None


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


class MsnWeather(SingleCoordinatorWeatherEntity[MsnWeatherCoordinator]):
    """MSN weather entity with daily, twice-daily and hourly forecasts."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_attribution = ATTRIBUTION
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.MBAR
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_native_visibility_unit = UnitOfLength.KILOMETERS
    _attr_native_precipitation_unit = UnitOfPrecipitationDepth.MILLIMETERS
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_DAILY
        | WeatherEntityFeature.FORECAST_HOURLY
        | WeatherEntityFeature.FORECAST_TWICE_DAILY
    )

    def __init__(self, coordinator: MsnWeatherCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_weather"
        self._attr_device_info = device_info(coordinator)
        self.entity_id = suggested_entity_id(coordinator, "weather", None)
        if coordinator.imperial:  # MSN is queried with units=F
            self._attr_native_temperature_unit = UnitOfTemperature.FAHRENHEIT
            self._attr_native_pressure_unit = UnitOfPressure.INHG
            self._attr_native_wind_speed_unit = UnitOfSpeed.MILES_PER_HOUR
            self._attr_native_visibility_unit = UnitOfLength.MILES
            self._attr_native_precipitation_unit = UnitOfPrecipitationDepth.INCHES

    @property
    def _cur(self) -> dict[str, Any]:
        return self.coordinator.data.current

    @property
    def condition(self) -> str | None:
        return condition_from_symbol(self._cur.get("symbol"), self._cur.get("wx"))

    @property
    def native_temperature(self) -> float | None:
        return self._cur.get("temp")

    @property
    def native_apparent_temperature(self) -> float | None:
        return self._cur.get("feels")

    @property
    def native_dew_point(self) -> float | None:
        return self._cur.get("dewPt")

    @property
    def humidity(self) -> float | None:
        return self._cur.get("rh")

    @property
    def native_pressure(self) -> float | None:
        return self._cur.get("baro")

    @property
    def native_wind_speed(self) -> float | None:
        return self._cur.get("windSpd")

    @property
    def native_wind_gust_speed(self) -> float | None:
        return self._cur.get("windGust")

    @property
    def wind_bearing(self) -> float | None:
        return self._cur.get("windDir")

    @property
    def native_visibility(self) -> float | None:
        return self._cur.get("vis")

    @property
    def uv_index(self) -> float | None:
        return self._cur.get("uv")

    @property
    def cloud_coverage(self) -> float | None:
        return self._cur.get("cloudCover")

    @property
    def ozone(self) -> float | None:
        return self.coordinator.data.aqi_params.get("curO3")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        cur = self._cur
        return {
            "condition_text": cur.get("cap"),
            "aqi": cur.get("aqi"),
            "aqi_severity": cur.get("aqiSeverity"),
            "provider": self.coordinator.data.provider,
            "observation_time": cur.get("created"),
        }

    # ---- forecasts -------------------------------------------------------

    @callback
    def _async_forecast_daily(self) -> list[Forecast] | None:
        out: list[Forecast] = []
        for day in self.coordinator.data.days:
            d = day.get("daily", {})
            start = parse_dt(d.get("valid"))
            if not start:
                continue
            out.append(
                Forecast(
                    datetime=_iso(start),
                    condition=condition_from_symbol(
                        d.get("symbol"), (d.get("day") or {}).get("wx")
                    ),
                    native_temperature=d.get("tempHi"),
                    native_templow=d.get("tempLo"),
                    native_apparent_temperature=d.get("feelsHi"),
                    native_dew_point=d.get("dewPt"),
                    humidity=d.get("rh"),
                    native_pressure=d.get("baro"),
                    native_precipitation=_sum(d.get("raToMN"), d.get("saToMN")),
                    precipitation_probability=d.get("precip"),
                    native_wind_speed=d.get("windMax"),
                    wind_bearing=d.get("windMaxDir"),
                    uv_index=d.get("uv"),
                    # Non-standard extras (kept by HA in the service response)
                    feels_like_low=d.get("feelsLo"),
                    humidity_high=d.get("rhHi"),
                    humidity_low=d.get("rhLo"),
                    visibility=d.get("vis"),
                    aqi=d.get("aqi"),
                    summary=(d.get("day") or {}).get("summary"),
                    **self._details(start),
                )
            )
        return out

    def _details(self, start: datetime) -> dict[str, Any]:
        det = self.coordinator.data.day_details.get(start.strftime("%Y-%m-%d"), {})
        extra: dict[str, Any] = {}
        if det.get("wind_gust") is not None:
            extra["native_wind_gust_speed"] = det["wind_gust"]
        if det.get("cloud_day") is not None:
            extra["cloud_coverage"] = round(det["cloud_day"])
        for key in (
            "feels_low", "wind_low", "wind_high", "pressure_high", "pressure_low",
            "visibility_high", "visibility_low", "cloud_night", "rain_day", "rain_night",
            "snow_day", "snow_night", "pollen_index", "pollen_main", "sunrise", "sunset",
            "moonrise", "moonset", "moonphase",
        ):
            if det.get(key) is not None:
                extra[key] = det[key]
        return extra

    @callback
    def _async_forecast_twice_daily(self) -> list[Forecast] | None:
        out: list[Forecast] = []
        for day in self.coordinator.data.days:
            d = day.get("daily", {})
            start = parse_dt(d.get("valid"))
            if not start:
                continue
            for part, hour, is_day, temp in (
                ("day", 7, True, d.get("tempHi")),
                ("night", 19, False, d.get("tempLo")),
            ):
                p = d.get(part) or {}
                out.append(
                    Forecast(
                        datetime=_iso(start + timedelta(hours=hour)),
                        is_daytime=is_day,
                        condition=condition_from_symbol(p.get("symbol"), p.get("wx")),
                        native_temperature=temp,
                        precipitation_probability=p.get("precip"),
                        native_wind_speed=p.get("windSpd"),
                        wind_bearing=p.get("windDir"),
                        summary=p.get("summary"),
                    )
                )
        return out

    @callback
    def _async_forecast_hourly(self) -> list[Forecast] | None:
        out: list[Forecast] = []
        for h in self.coordinator.data.hourly:
            start = parse_dt(h.get("valid"))
            if not start:
                continue
            out.append(
                Forecast(
                    datetime=_iso(start),
                    is_daytime=(h.get("symbol") or "d")[0] != "n",
                    condition=condition_from_symbol(h.get("symbol"), h.get("wx")),
                    native_temperature=h.get("temp"),
                    native_apparent_temperature=h.get("feels"),
                    native_dew_point=h.get("dewPt"),
                    humidity=h.get("rh"),
                    native_pressure=h.get("baro"),
                    native_precipitation=_sum(h.get("rainAmount"), h.get("snowAmount")),
                    precipitation_probability=h.get("precip"),
                    native_wind_speed=h.get("windSpd"),
                    native_wind_gust_speed=h.get("windGust"),
                    wind_bearing=h.get("windDir"),
                    cloud_coverage=h.get("cloudCover"),
                    uv_index=h.get("uv"),
                    visibility=h.get("vis"),
                    aqi=h.get("aqi"),
                )
            )
        return out
