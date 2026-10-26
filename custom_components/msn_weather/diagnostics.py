"""Diagnostics download – location, name, secrets and keys are redacted."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant

from .const import CONF_API_KEY, CONF_IMAGE_SECRET, DEFAULT_API_KEY
from .coordinator import MsnWeatherConfigEntry

TO_REDACT = {CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME, CONF_API_KEY, CONF_IMAGE_SECRET, "title", "unique_id"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: MsnWeatherConfigEntry
) -> dict[str, Any]:
    coordinator = entry.runtime_data
    data = coordinator.data
    summary: dict[str, Any] = {}
    if data is not None:
        summary = {
            "fetched": data.fetched.isoformat() if data.fetched else None,
            "provider": data.provider,
            "imperial": data.imperial,
            "current_fields": sorted(data.current),
            "days": len(data.days),
            "hourly": len(data.hourly),
            "alerts": len(data.alerts),
            "insights": sorted(data.insights),
            "life_today": sorted(data.life_today),
            "day_details": len(data.day_details),
            "aqi_forecast": len(data.aqi_forecast),
            "climate": bool(data.climate),
            "monthly": len(data.monthly),
            "storms": len(data.storms),
            "storms_visible": len(data.storms_visible),
            "nowcast": {
                "template_type": data.nowcast.get("templateType"),
                "values": len(data.nowcast.get("precipitation") or []),
            },
        }
    meta = coordinator.map_renderer._metadata or {}  # noqa: SLF001 - diagnostics only
    return {
        "entry": async_redact_data(
            {"data": dict(entry.data), "options": dict(entry.options), "version": entry.version}, TO_REDACT
        ),
        "language": coordinator.language,
        "update_success": coordinator.last_update_success,
        "last_exception": repr(coordinator.last_exception) if coordinator.last_exception else None,
        "api_key": "default" if coordinator.client.api_key == DEFAULT_API_KEY else "custom or discovered",
        "data": summary,
        "map_layers_available": sorted(k for k, v in meta.items() if isinstance(v, dict) and v.get("uris")),
        "map_offset_hours": coordinator.map_offset,
        "cyclone_selection": coordinator.cyclone_selection,
    }
