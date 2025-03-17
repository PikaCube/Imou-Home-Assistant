import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyimouapi.exceptions import ImouException

from .const import DOMAIN
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
            _LOGGER.info(f"translation_key is {switch_entity.translation_key},unique_key is {switch_entity.unique_id}")
    if len(entities) > 0:
        async_add_entities(entities)


class ImouSwitch(ImouEntity, SwitchEntity):
    """imou switch."""

    async def async_turn_on(self, **kwargs: Any) -> None:  # noqa: D102
        try:
            await self.coordinator.device_manager.async_switch_operation(
                self._device, self._entity_type, True
            )
            self.async_write_ha_state()
        except ImouException as e:
            raise HomeAssistantError(e.message)  # noqa: B904

    async def async_turn_off(self, **kwargs: Any) -> None:  # noqa: D102
        try:
            _LOGGER.info(self.coordinator.hass.config.language)
            await self.coordinator.device_manager.async_switch_operation(
                self._device, self._entity_type, False
            )
            self.async_write_ha_state()
        except ImouException as e:
            raise HomeAssistantError(e.message)  # noqa: B904

    @property
    def is_on(self) -> bool | None:  # noqa: D102
        return self._device.switches[self._entity_type]
