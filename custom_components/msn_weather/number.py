"""Number entity: forecast hour shown on the weather maps."""

from __future__ import annotations

from homeassistant.components.number import NumberMode, RestoreNumber
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_MAP_ZOOM, DEFAULT_MAP_ZOOM
from .coordinator import MsnWeatherConfigEntry, MsnWeatherCoordinator
from .entity import MsnWeatherEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MsnWeatherConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([MsnMapForecastHours(entry.runtime_data), MsnMapZoom(entry.runtime_data)])


class MsnMapForecastHours(MsnWeatherEntity, RestoreNumber):
    """0 = now; 1..240 = hours ahead for the forecast-capable map layers."""

    _platform_domain = "number"
    _attr_translation_key = "map_forecast_hours"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = 0
    _attr_native_max_value = 240
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_icon = "mdi:map-clock"

    def __init__(self, coordinator: MsnWeatherCoordinator) -> None:
        super().__init__(coordinator, "map_forecast_hours")

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_number_data()
        if last and last.native_value is not None:
            self.coordinator.map_offset = int(last.native_value)

    @property
    def native_value(self) -> float:
        return self.coordinator.map_offset

    async def async_set_native_value(self, value: float) -> None:
        self.coordinator.map_offset = int(value)
        # notify all entities (the map images reload)
        self.coordinator.async_update_listeners()


class MsnMapZoom(MsnWeatherEntity, RestoreNumber):
    """Zoom of all weather maps (3 = continent … 11 = local), adjustable live."""

    _platform_domain = "number"
    _attr_translation_key = "map_zoom"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = 3
    _attr_native_max_value = 11
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:magnify-plus-outline"

    def __init__(self, coordinator: MsnWeatherCoordinator) -> None:
        super().__init__(coordinator, "map_zoom")

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_number_data()
        state = await self.async_get_last_state()
        # keep the live value unless the zoom in the integration options was changed since
        if (
            last and last.native_value is not None and state
            and state.attributes.get("options_zoom") == self._options_zoom
        ):
            self.coordinator.map_zoom = int(last.native_value)

    @property
    def _options_zoom(self) -> int:
        return int(self.coordinator.config_entry.options.get(CONF_MAP_ZOOM, DEFAULT_MAP_ZOOM))

    @property
    def extra_state_attributes(self) -> dict[str, int]:
        return {"options_zoom": self._options_zoom}

    @property
    def native_value(self) -> float:
        return self.coordinator.map_zoom

    async def async_set_native_value(self, value: float) -> None:
        self.coordinator.map_zoom = int(value)
        self.coordinator.async_update_listeners()
