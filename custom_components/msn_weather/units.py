"""Unit handling: MSN is queried in the Home Assistant unit system (metric or US customary)."""

from __future__ import annotations

from homeassistant.const import (
    UnitOfLength,
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)

IMPERIAL_UNITS: dict[str, str] = {
    UnitOfTemperature.CELSIUS: UnitOfTemperature.FAHRENHEIT,
    UnitOfSpeed.KILOMETERS_PER_HOUR: UnitOfSpeed.MILES_PER_HOUR,
    UnitOfPressure.MBAR: UnitOfPressure.INHG,
    UnitOfPressure.HPA: UnitOfPressure.INHG,
    UnitOfLength.KILOMETERS: UnitOfLength.MILES,
    UnitOfPrecipitationDepth.MILLIMETERS: UnitOfPrecipitationDepth.INCHES,
}

# decimals that make sense for the imperial units
IMPERIAL_PRECISION: dict[str, int] = {
    UnitOfPressure.INHG: 2,
    UnitOfPrecipitationDepth.INCHES: 2,
    UnitOfLength.MILES: 1,
}

KM_PER_MILE = 1.609344


def msn_unit(unit: str | None, imperial: bool) -> str | None:
    """Unit in which MSN delivers a value that is `unit` in metric mode."""
    if not imperial or unit is None:
        return unit
    return IMPERIAL_UNITS.get(unit, unit)


def kmh(value: float | None, imperial: bool) -> float | None:
    """km/h (storm data is always metric) -> display unit."""
    if value is None or not imperial:
        return value
    return round(value / KM_PER_MILE)
