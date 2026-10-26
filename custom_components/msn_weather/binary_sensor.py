"""Binary sensor: active severe weather warning."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .api import parse_dt
from .coordinator import MsnWeatherConfigEntry, MsnWeatherCoordinator
from .entity import MsnWeatherEntity
from .sensor import _alert_list


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MsnWeatherConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([MsnAlertActive(entry.runtime_data), MsnCycloneNearby(entry.runtime_data)])


class MsnAlertActive(MsnWeatherEntity, BinarySensorEntity):
    """On while at least one warning is in effect right now."""

    _platform_domain = "binary_sensor"
    _attr_device_class = BinarySensorDeviceClass.SAFETY
    _attr_translation_key = "alert_active"

    def __init__(self, coordinator: MsnWeatherCoordinator) -> None:
        super().__init__(coordinator, "alert_active")

    def _active(self) -> list[dict[str, Any]]:
        now = dt_util.now()
        out = []
        for alert in self.coordinator.data.alerts:
            start, end = parse_dt(alert.get("start")), parse_dt(alert.get("end"))
            if (start is None or start <= now) and (end is None or now <= end):
                out.append(alert)
        return out

    @property
    def is_on(self) -> bool:
        return bool(self._active())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        active = self._active()
        return {
            "active": [a.get("title") for a in active],
            "highest_level": active[0].get("level") if active else None,
            "all_alerts": _alert_list(self.coordinator.data),
        }


class MsnCycloneNearby(MsnWeatherEntity, BinarySensorEntity):
    """On while a tropical cyclone is (or is forecast to come) within the configured radius."""

    _platform_domain = "binary_sensor"
    _attr_device_class = BinarySensorDeviceClass.SAFETY
    _attr_translation_key = "cyclone_nearby"

    def __init__(self, coordinator: MsnWeatherCoordinator) -> None:
        super().__init__(coordinator, "cyclone_nearby")

    def _storms(self) -> list[dict[str, Any]]:
        return [s for s in self.coordinator.data.storms_visible if not s["disturbance"]]

    @property
    def is_on(self) -> bool:
        return bool(self._storms())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        storms = self._storms()
        return {
            "storms": [s.get("name") for s in storms],
            "closest_km": min((s["closest_km"] for s in storms if s.get("closest_km") is not None), default=None),
        }
