"""Base entity for MSN Weather."""

from __future__ import annotations

import base64
import json
from urllib.parse import quote

from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import ATTRIBUTION, DEFAULT_NAME, DOMAIN
from .coordinator import MsnWeatherCoordinator


def device_info(coordinator: MsnWeatherCoordinator) -> DeviceInfo:
    entry = coordinator.config_entry
    lang = coordinator.language
    name = entry.data.get(CONF_NAME, DEFAULT_NAME)
    loc = base64.b64encode(
        json.dumps(
            {
                "l": name,
                "g": lang,
                "x": str(entry.data[CONF_LONGITUDE]),
                "y": str(entry.data[CONF_LATITUDE]),
            }
        ).encode()
    ).decode()
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=name,
        manufacturer="Microsoft",
        model="MSN Weather",
        entry_type=DeviceEntryType.SERVICE,
        configuration_url=(
            f"https://www.msn.com/{lang}/weather/forecast/in-{quote(name)}"
            f"?loc={quote(loc)}&weadegreetype={'F' if coordinator.imperial else 'C'}"
        ),
    )


def suggested_entity_id(coordinator: MsnWeatherCoordinator, domain: str, key: str | None) -> str:
    """Language independent entity id, e.g. ``sensor.upper_east_side_umbrella``.

    Home Assistant would otherwise derive the id from the translated name, so the
    same sensor would be ``sensor.upper_east_side_regenschirm`` on a German installation.
    Only used when the entity is registered for the first time.
    """
    base = slugify(coordinator.config_entry.data.get(CONF_NAME) or coordinator.config_entry.title or DEFAULT_NAME)
    return f"{domain}.{base}_{key}" if key else f"{domain}.{base}"


class MsnWeatherEntity(CoordinatorEntity[MsnWeatherCoordinator]):
    """Common base."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION
    #: platform domain, set by the subclasses (sensor, image, …)
    _platform_domain: str = "sensor"

    def __init__(self, coordinator: MsnWeatherCoordinator, key: str, object_key: str | None = None) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{key}"
        self._attr_device_info = device_info(coordinator)
        self.entity_id = suggested_entity_id(coordinator, self._platform_domain, object_key or key)
