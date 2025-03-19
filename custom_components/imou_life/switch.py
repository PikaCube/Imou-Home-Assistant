import logging
from typing import Any

import voluptuous as vol
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyimouapi.exceptions import ImouException

from .const import DOMAIN, PARAM_ENTITY_ID, SERVICE_TURN_ON, SERVICE_TURN_OFF
from .entity import ImouEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(  # noqa: D103
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    _LOGGER.info("ImouSwitch.async_setup_entry")
    imou_coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for device in imou_coordinator.devices:
        for switch_type in device.switches:
            switch_entity = ImouSwitch(imou_coordinator, entry, switch_type, device)
            entities.append(switch_entity)
            _LOGGER.debug(
                f"translation_key is {switch_entity.translation_key},unique_key is {switch_entity.unique_id}"
            )
    if len(entities) > 0:
        async_add_entities(entities)

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_TURN_ON,
        {
            vol.Required(PARAM_ENTITY_ID): cv.entity_id,
        },
        "async_turn_on",
    )
    platform.async_register_entity_service(
        SERVICE_TURN_OFF,
        {
            vol.Required(PARAM_ENTITY_ID): cv.entity_id,
        },
        "async_turn_off",
    )


class ImouSwitch(ImouEntity, SwitchEntity):
    """imou switch."""

    async def async_turn_on(self, **kwargs: Any) -> None:  # noqa: D102
        try:
            await self._coordinator.device_manager.async_switch_operation(
                self._device, self._entity_type, True
            )
            self.async_write_ha_state()
        except ImouException as e:
            raise HomeAssistantError(e.message)  # noqa: B904

    async def async_turn_off(self, **kwargs: Any) -> None:  # noqa: D102
        try:
            await self._coordinator.device_manager.async_switch_operation(
                self._device, self._entity_type, False
            )
            self.async_write_ha_state()
        except ImouException as e:
            raise HomeAssistantError(e.message)  # noqa: B904

    @property
    def is_on(self) -> bool | None:  # noqa: D102
        return self._device.switches[self._entity_type]
