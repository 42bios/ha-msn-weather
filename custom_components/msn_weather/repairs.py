"""Repair flow: enter a new API key when MSN rejected the current one."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import data_entry_flow
from homeassistant.components.repairs import RepairsFlow
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector

from .api import MsnWeatherAuthError, MsnWeatherClient, MsnWeatherError
from .const import CONF_API_KEY, CONF_LANGUAGE, DEFAULT_LANGUAGE, DOMAIN
from .coordinator import async_load_shared


class ApiKeyRepairFlow(RepairsFlow):
    """Ask for the API key, check it and use it for all entries."""

    def __init__(self, entry_id: str | None) -> None:
        self._entry_id = entry_id

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> data_entry_flow.FlowResult:
        entry = (
            self.hass.config_entries.async_get_entry(self._entry_id) if self._entry_id else None
        )
        errors: dict[str, str] = {}
        if user_input is not None:
            key = user_input[CONF_API_KEY].strip()
            data = entry.data if entry else {}
            client = MsnWeatherClient(
                async_get_clientsession(self.hass),
                data.get(CONF_LATITUDE, self.hass.config.latitude),
                data.get(CONF_LONGITUDE, self.hass.config.longitude),
                data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE),
                key,
            )
            try:
                await client.async_get()
            except MsnWeatherAuthError:
                errors[CONF_API_KEY] = "invalid_auth"
            except MsnWeatherError:
                errors["base"] = "cannot_connect"
            else:
                # The key belongs to msn.com, not to one entry: keep it like a key the
                # integration found itself, so later rotations are handled automatically.
                shared = await async_load_shared(self.hass)
                await shared.async_set_api_key(key)
                for other in self.hass.config_entries.async_entries(DOMAIN):
                    issue_id = f"api_key_{other.entry_id}"
                    rejected = other.entry_id == self._entry_id or (
                        ir.async_get(self.hass).async_get_issue(DOMAIN, issue_id) is not None
                    )
                    if not rejected:
                        continue
                    ir.async_delete_issue(self.hass, DOMAIN, issue_id)
                    reloads_itself = False
                    if CONF_API_KEY in other.options:
                        # the rejected key from the options would win over the new one
                        reloads_itself = other.state is ConfigEntryState.LOADED
                        self.hass.config_entries.async_update_entry(
                            other,
                            options={k: v for k, v in other.options.items() if k != CONF_API_KEY},
                        )
                    if not reloads_itself:
                        self.hass.config_entries.async_schedule_reload(other.entry_id)
                return self.async_create_entry(data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): TextSelector()}),
            errors=errors,
            description_placeholders={"name": entry.title if entry else "MSN Weather"},
        )


async def async_create_fix_flow(
    hass: HomeAssistant, issue_id: str, data: dict[str, str | int | float | None] | None
) -> RepairsFlow:
    return ApiKeyRepairFlow((data or {}).get("entry_id"))
