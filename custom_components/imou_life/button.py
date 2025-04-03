"""Support for Imou button controls."""

import logging

import voluptuous as vol
from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyimouapi.const import PARAM_DURATION
from pyimouapi.exceptions import ImouException

from .const import (
    DOMAIN,
    PARAM_RESTART_DEVICE,
    PARAM_ROTATION_DURATION,
    SERVICE_CONTROL_MOVE_PTZ,
    PARAM_PTZ,
    PARAM_ENTITY_ID,
    SERVICE_RESTART_DEVICE,
)
from .entity import ImouEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up button."""
    _LOGGER.info("ImouButton.async_setup_entry")
    imou_coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for device in imou_coordinator.devices:
        for button_type in device.buttons:
            button_entity = ImouButton(imou_coordinator, entry, button_type, device)
            entities.append(button_entity)
    if len(entities) > 0:
        async_add_entities(entities)

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_CONTROL_MOVE_PTZ,
        {
            vol.Required(PARAM_ENTITY_ID): cv.entity_id,
            vol.Required(PARAM_DURATION): vol.All(
                vol.Coerce(int), vol.Range(min=100, max=10000)
            ),
        },
        "async_handle_control_move_ptz",
    )
    platform.async_register_entity_service(
        SERVICE_RESTART_DEVICE,
        {
            vol.Required(PARAM_ENTITY_ID): cv.entity_id,
        },
        "async_handle_restart_device",
    )


class ImouButton(ImouEntity, ButtonEntity):
    """imou button."""

    async def async_press(self) -> None:
        """Handle button press."""
        await self._async_do_press(
            self._config_entry.options.get(PARAM_ROTATION_DURATION, 500)
        )

    @property
    def device_class(self) -> ButtonDeviceClass | None:
        if self._entity_type == PARAM_RESTART_DEVICE:
            return ButtonDeviceClass.RESTART
        return None

    async def async_handle_control_move_ptz(self, duration: int):
        _LOGGER.debug(
            f"async_handle_control_move_ptz duration is {duration},entity_type is{self._entity_type}"
        )
        if PARAM_PTZ not in self._entity_type:
            raise HomeAssistantError(
                f"Invalid entity type {self._entity_type},it must be ptz button"
            )
        await self._async_do_press(duration)

    async def async_handle_restart_device(self):
        _LOGGER.debug(f"async_handle_restart_device,entity_type is{self._entity_type}")
        if PARAM_RESTART_DEVICE != self._entity_type:
            raise HomeAssistantError(
                f"Invalid entity type {self._entity_type},it must be restart_device button"
            )
        await self._async_do_press(0)

    async def _async_do_press(self, duration: int):
        try:
            await self._coordinator.device_manager.async_press_button(
                self._device,
                self._entity_type,
                duration,
            )
        except ImouException as e:
            raise HomeAssistantError(e.message)  # noqa: B904
