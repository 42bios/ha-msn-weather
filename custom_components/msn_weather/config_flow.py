"""Config flow for MSN Weather."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntryState, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM
from homeassistant.helpers.selector import (
    BooleanSelector,
    LocationSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
)

from .api import MsnWeatherAuthError, MsnWeatherClient, MsnWeatherError, parse_msn_url
from .coordinator import automatic_api_key
from .const import (
    CONF_API_KEY,
    CONF_CYCLONE_DISTURBANCES,
    CONF_CYCLONE_FOCUS,
    CONF_CYCLONE_RADIUS,
    CONF_LANGUAGE,
    CONF_MAP_FRAME_MS,
    CONF_MAP_FRAMES,
    CONF_MAP_HEIGHT,
    CONF_MAP_HIRES,
    CONF_MAP_LABELS,
    CONF_MAP_WIDTH,
    CONF_MAP_ZOOM,
    CONF_MSN_URL,
    CONF_SCAN_INTERVAL,
    CONF_USE_HOME,
    DEFAULT_API_KEY,
    DEFAULT_CYCLONE_FOCUS,
    DEFAULT_CYCLONE_RADIUS,
    DEFAULT_LANGUAGE,
    DEFAULT_MAP_FRAME_MS,
    DEFAULT_MAP_FRAMES,
    DEFAULT_MAP_HEIGHT,
    DEFAULT_MAP_WIDTH,
    DEFAULT_MAP_ZOOM,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LANGUAGES,
    MIN_SCAN_INTERVAL,
)


_LANG_DEFAULTS = {"de": "de-de", "en": "en-us", "it": "it-it", "fr": "fr-fr", "es": "es-es", "nl": "nl-nl"}


def _ha_language(hass) -> str:
    """MSN market matching the Home Assistant language (and country, if available)."""
    lang = (hass.config.language or "").lower().replace("_", "-")
    if lang in LANGUAGES:
        return lang
    base = lang.split("-")[0]
    country = (getattr(hass.config, "country", None) or "").lower()
    if f"{base}-{country}" in LANGUAGES:
        return f"{base}-{country}"
    return _LANG_DEFAULTS.get(base, DEFAULT_LANGUAGE)


class MsnWeatherConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            name, lat, lon, use_home = self._location(user_input, errors)

            if not errors:
                language = user_input[CONF_LANGUAGE]
                client = MsnWeatherClient(
                    async_get_clientsession(self.hass), lat, lon, language, automatic_api_key(self.hass)
                )
                try:
                    data = await client.async_get()
                except MsnWeatherAuthError:
                    errors["base"] = "invalid_auth"
                except MsnWeatherError:
                    errors["base"] = "cannot_connect"
                else:
                    await self.async_set_unique_id(f"{lat:.3f}_{lon:.3f}_{language}")
                    self._abort_if_unique_id_configured()
                    title = name or data.location.get("name") or self.hass.config.location_name or "MSN Weather"
                    return self.async_create_entry(
                        title=title,
                        data={
                            CONF_NAME: title,
                            CONF_LATITUDE: lat,
                            CONF_LONGITUDE: lon,
                            CONF_LANGUAGE: language,
                            # follow the Home Assistant location (also when it changes later)
                            CONF_USE_HOME: use_home,
                        },
                    )

        schema = vol.Schema(
            {
                vol.Optional(CONF_NAME): TextSelector(),
                vol.Required(CONF_USE_HOME, default=True): BooleanSelector(),
                vol.Optional(
                    CONF_LOCATION,
                    default={
                        CONF_LATITUDE: self.hass.config.latitude,
                        CONF_LONGITUDE: self.hass.config.longitude,
                    },
                ): LocationSelector(),
                vol.Optional(CONF_MSN_URL): TextSelector(),
                vol.Required(CONF_LANGUAGE, default=_ha_language(self.hass)): SelectSelector(
                    SelectSelectorConfig(
                        options=LANGUAGES, mode=SelectSelectorMode.DROPDOWN, custom_value=True
                    )
                ),
            }
        )
        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(schema, user_input or {}),
            errors=errors,
        )

    def _location(
        self, user_input: dict[str, Any], errors: dict[str, str]
    ) -> tuple[str | None, float, float, bool]:
        """Name, coordinates and "follow the Home Assistant location" from the form."""
        name = user_input.get(CONF_NAME)
        lat, lon = self.hass.config.latitude, self.hass.config.longitude
        url = (user_input.get(CONF_MSN_URL) or "").strip()
        if url:
            parsed = parse_msn_url(url)
            if parsed is None:
                errors[CONF_MSN_URL] = "invalid_url"
            else:
                lat, lon, place = parsed
                name = name or place
        elif not user_input.get(CONF_USE_HOME, True):
            loc = user_input.get(CONF_LOCATION) or {}
            lat = loc.get(CONF_LATITUDE, lat)
            lon = loc.get(CONF_LONGITUDE, lon)
        return name, lat, lon, not url and bool(user_input.get(CONF_USE_HOME, True))

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Change the location or the name of an entry; entities and their ids stay."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            name, lat, lon, use_home = self._location(user_input, errors)
            if not errors:
                language = entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
                client = MsnWeatherClient(
                    async_get_clientsession(self.hass), lat, lon, language,
                    entry.options.get(CONF_API_KEY) or automatic_api_key(self.hass),
                )
                try:
                    data = await client.async_get()
                except MsnWeatherAuthError:
                    errors["base"] = "invalid_auth"
                except MsnWeatherError:
                    errors["base"] = "cannot_connect"
                else:
                    unique_id = f"{lat:.3f}_{lon:.3f}_{language}"
                    if any(
                        other.unique_id == unique_id and other.entry_id != entry.entry_id
                        for other in self._async_current_entries()
                    ):
                        return self.async_abort(reason="already_configured")
                    title = name or data.location.get("name") or entry.title
                    # a loaded entry reloads itself through its update listener
                    reloads_itself = entry.state is ConfigEntryState.LOADED
                    changed = self.hass.config_entries.async_update_entry(
                        entry,
                        unique_id=unique_id,
                        title=title,
                        data={
                            **entry.data,
                            CONF_NAME: title,
                            CONF_LATITUDE: lat,
                            CONF_LONGITUDE: lon,
                            CONF_USE_HOME: use_home,
                        },
                    )
                    if not (changed and reloads_itself):
                        self.hass.config_entries.async_schedule_reload(entry.entry_id)
                    return self.async_abort(reason="reconfigure_successful")

        schema = vol.Schema(
            {
                vol.Optional(CONF_NAME): TextSelector(),
                vol.Required(CONF_USE_HOME): BooleanSelector(),
                vol.Optional(CONF_LOCATION): LocationSelector(),
                vol.Optional(CONF_MSN_URL): TextSelector(),
            }
        )
        current = {
            CONF_NAME: entry.data.get(CONF_NAME) or entry.title,
            CONF_USE_HOME: bool(entry.data.get(CONF_USE_HOME)),
            CONF_LOCATION: {
                CONF_LATITUDE: entry.data[CONF_LATITUDE],
                CONF_LONGITUDE: entry.data[CONF_LONGITUDE],
            },
        }
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(schema, user_input or current),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> MsnWeatherOptionsFlow:
        return MsnWeatherOptionsFlow()


class MsnWeatherOptionsFlow(OptionsFlow):
    """Options: polling interval and API key."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        automatic_key = automatic_api_key(self.hass)
        if user_input is not None:
            # store the key only when the user entered one of their own
            key = (user_input.pop(CONF_API_KEY, None) or "").strip()
            if key and key not in (automatic_key, DEFAULT_API_KEY):
                user_input[CONF_API_KEY] = key
            return self.async_create_entry(data=user_input)

        options = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_LANGUAGE,
                    default=options.get(CONF_LANGUAGE)
                    or self.config_entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE),
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=LANGUAGES, mode=SelectSelectorMode.DROPDOWN, custom_value=True
                    )
                ),
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=MIN_SCAN_INTERVAL,
                        max=240,
                        step=1,
                        unit_of_measurement="min",
                        mode=NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_MAP_ZOOM, default=options.get(CONF_MAP_ZOOM, DEFAULT_MAP_ZOOM)
                ): NumberSelector(
                    NumberSelectorConfig(min=3, max=11, step=1, mode=NumberSelectorMode.SLIDER)
                ),
                vol.Required(
                    CONF_MAP_WIDTH, default=options.get(CONF_MAP_WIDTH, DEFAULT_MAP_WIDTH)
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=300, max=1920, step=10, unit_of_measurement="px",
                        mode=NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_MAP_HEIGHT, default=options.get(CONF_MAP_HEIGHT, DEFAULT_MAP_HEIGHT)
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=200, max=1080, step=10, unit_of_measurement="px",
                        mode=NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_MAP_FRAMES, default=options.get(CONF_MAP_FRAMES, DEFAULT_MAP_FRAMES)
                ): NumberSelector(
                    NumberSelectorConfig(min=1, max=24, step=1, mode=NumberSelectorMode.SLIDER)
                ),
                vol.Required(
                    CONF_MAP_HIRES, default=options.get(CONF_MAP_HIRES, True)
                ): BooleanSelector(),
                vol.Required(
                    CONF_MAP_FRAME_MS, default=options.get(CONF_MAP_FRAME_MS, DEFAULT_MAP_FRAME_MS)
                ): NumberSelector(
                    NumberSelectorConfig(min=150, max=3000, step=50, unit_of_measurement="ms", mode=NumberSelectorMode.SLIDER)
                ),
                vol.Required(
                    CONF_MAP_LABELS, default=options.get(CONF_MAP_LABELS, True)
                ): BooleanSelector(),
                vol.Required(
                    CONF_CYCLONE_RADIUS,
                    default=options.get(CONF_CYCLONE_RADIUS, DEFAULT_CYCLONE_RADIUS),
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=0, max=20000, step=100,
                        unit_of_measurement="mi" if self.hass.config.units is US_CUSTOMARY_SYSTEM else "km",
                        mode=NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_CYCLONE_FOCUS,
                    default=options.get(CONF_CYCLONE_FOCUS, DEFAULT_CYCLONE_FOCUS),
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=["strongest", "nearest"],
                        mode=SelectSelectorMode.LIST,
                        translation_key="cyclone_focus",
                    )
                ),
                vol.Required(
                    CONF_CYCLONE_DISTURBANCES,
                    default=options.get(CONF_CYCLONE_DISTURBANCES, True),
                ): BooleanSelector(),
                vol.Optional(
                    CONF_API_KEY,
                    description={"suggested_value": options.get(CONF_API_KEY) or automatic_key},
                ): TextSelector(),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
