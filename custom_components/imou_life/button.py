"""Support for Imou button controls."""

import logging

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyimouapi.exceptions import ImouException

from .const import DOMAIN, PARAM_RESTART_DEVICE, PARAM_ROTATION_DURATION
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
            _LOGGER.debug(
                f"translation_key is {button_entity.translation_key},unique_key is {button_entity.unique_id}"
            )
            entities.append(button_entity)
    if len(entities) > 0:
        async_add_entities(entities)


class ImouButton(ImouEntity, ButtonEntity):
    """imou button."""

    async def async_press(self) -> None:
        """Handle button press."""
        try:
            await self.coordinator.device_manager.async_press_button(
                self._device,
                self._entity_type,
                self.config_entry.options.get(PARAM_ROTATION_DURATION, 500),
            )
        except ImouException as e:
            raise HomeAssistantError(e.message)  # noqa: B904

    @property
    def device_class(self) -> ButtonDeviceClass | None:
        if self._entity_type == PARAM_RESTART_DEVICE:
            return ButtonDeviceClass.RESTART
        return None
