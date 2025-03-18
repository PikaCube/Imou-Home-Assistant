"""config flow for Imou."""

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from pyimouapi.exceptions import ImouException
from pyimouapi.openapi import ImouOpenApiClient

from .const import (
    CONF_API_URL_FK,
    CONF_API_URL_OR,
    CONF_API_URL_SG,
    DOMAIN,
    PARAM_API_URL,
    PARAM_APP_ID,
    PARAM_APP_SECRET,
    CONF_API_URL_HZ,
    PARAM_UPDATE_INTERVAL,
    PARAM_DOWNLOAD_SNAP_WAIT_TIME,
    PARAM_LIVE_RESOLUTION,
    CONF_HD,
    CONF_SD,
    PARAM_ROTATION_DURATION,
    CONF_HTTPS,
    CONF_HTTP,
    PARAM_LIVE_PROTOCOL,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class ImouConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for imou."""

    def __init__(self) -> None:
        """Init ImouConfigFlow."""
        self._api_url = None
        self._app_id = None
        self._app_secret = None
        self._api_client = None
        self._session = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Set up user."""
        # USER INPUT IS EMPTY RETURN TO FORM
        if user_input is None:
            return self.async_show_form(
                step_id="login",
                data_schema=vol.Schema(
                    {
                        vol.Required(PARAM_APP_ID): str,
                        vol.Required(PARAM_APP_SECRET): str,
                        vol.Required(PARAM_API_URL, default=CONF_API_URL_SG): vol.In(
                            [
                                CONF_API_URL_SG,
                                CONF_API_URL_OR,
                                CONF_API_URL_FK,
                                CONF_API_URL_HZ,
                            ]
                        ),
                    }
                ),
            )
        # USER INPUT IS NOT EMPTY START LOGIN
        return await self.async_step_login(user_input)

    async def async_step_login(self, user_input) -> ConfigFlowResult:
        """Step login."""
        await self.async_set_unique_id(user_input[PARAM_APP_ID])
        self._abort_if_unique_id_configured()
        api_client = ImouOpenApiClient(
            user_input[PARAM_APP_ID],
            user_input[PARAM_APP_SECRET],
            user_input[PARAM_API_URL],
        )
        errors = {}
        try:
            await api_client.async_get_token()
            data = {
                PARAM_APP_ID: user_input[PARAM_APP_ID],
                PARAM_APP_SECRET: user_input[PARAM_APP_SECRET],
                PARAM_API_URL: user_input[PARAM_API_URL],
            }
            return self.async_create_entry(title=DOMAIN, data=data)
        except ImouException as exception:
            errors["base"] = exception.get_title()
            return self.async_show_form(
                step_id="login",
                data_schema=vol.Schema(
                    {
                        vol.Required(PARAM_APP_ID): str,
                        vol.Required(PARAM_APP_SECRET): str,
                        vol.Required(PARAM_API_URL, default=CONF_API_URL_SG): vol.In(
                            [
                                CONF_API_URL_SG,
                                CONF_API_URL_OR,
                                CONF_API_URL_FK,
                                CONF_API_URL_HZ,
                            ]
                        ),
                    }
                ),
                errors=errors,
            )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return ImouOptionsFlow()


class ImouOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(
                    {
                        vol.Required(PARAM_UPDATE_INTERVAL, default=60): int,
                        vol.Required(PARAM_DOWNLOAD_SNAP_WAIT_TIME, default=3): int,
                        vol.Required(PARAM_LIVE_RESOLUTION, default=CONF_HD): vol.In(
                            [CONF_HD, CONF_SD]
                        ),
                        vol.Required(PARAM_LIVE_PROTOCOL, default=CONF_HTTPS): vol.In(
                            [CONF_HTTPS, CONF_HTTP]
                        ),
                        vol.Required(PARAM_ROTATION_DURATION, default=500): int,
                    }
                ),
                self.config_entry.options,
            ),
        )
