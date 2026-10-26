"""Select entity: which tropical cyclone the cyclone map follows."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import CYCLONE_AUTO
from .coordinator import MsnWeatherConfigEntry, MsnWeatherCoordinator
from .entity import MsnWeatherEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MsnWeatherConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([MsnCycloneSelect(entry.runtime_data)])


class MsnCycloneSelect(MsnWeatherEntity, SelectEntity, RestoreEntity):
    """"auto" (strongest / nearest storm, see options) or a storm by name."""

    _platform_domain = "select"
    _attr_translation_key = "cyclone_map_storm"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:weather-hurricane"

    def __init__(self, coordinator: MsnWeatherCoordinator) -> None:
        super().__init__(coordinator, "cyclone_map_storm")

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last and last.state not in (None, "unknown", "unavailable"):
            # kept even if the storm is not active right now; falls back to auto
            self.coordinator.cyclone_selection = last.state

    @property
    def options(self) -> list[str]:
        storms = self.coordinator.data.storms_visible if self.coordinator.data else []
        names = [s["name"] for s in storms if not s["disturbance"] and s.get("name")]
        return [CYCLONE_AUTO, *dict.fromkeys(names)]

    @property
    def current_option(self) -> str:
        sel = self.coordinator.cyclone_selection
        return sel if sel in self.options else CYCLONE_AUTO

    async def async_select_option(self, option: str) -> None:
        self.coordinator.cyclone_selection = option
        # notify all entities (the cyclone map re-renders)
        self.coordinator.async_update_listeners()
