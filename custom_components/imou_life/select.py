import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyimouapi.exceptions import ImouException

from .const import DOMAIN, PARAM_CURRENT_OPTION, PARAM_OPTIONS
from .entity import ImouEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(  # noqa: D103
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    _LOGGER.info("ImouSelect.async_setup_entry")
    imou_coordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[ImouSelect] = []
    for device in imou_coordinator.devices:
        for select_type in device.selects:
            select_entity = ImouSelect(imou_coordinator, entry, select_type, device)
            _LOGGER.debug(
                f"translation_key is {select_entity.translation_key},unique_key is {select_entity.unique_id}"
            )
            entities.append(select_entity)
    if len(entities) > 0:
        async_add_entities(entities)


class ImouSelect(ImouEntity, SelectEntity):
    """imou select."""

    @property
    def options(self) -> list[str]:  # noqa: D102
        return self._device.selects[self._entity_type][PARAM_OPTIONS]

    @property
    def current_option(self) -> str | None:  # noqa: D102
        return self._device.selects[self._entity_type][PARAM_CURRENT_OPTION]

    async def async_select_option(self, option: str) -> None:  # noqa: D102
        try:
            await self.coordinator.device_manager.async_select_option(
                self._device, self._entity_type, option
            )
            self._device.selects[self._entity_type][PARAM_CURRENT_OPTION] = option
            self.async_write_ha_state()
        except ImouException as e:
            raise HomeAssistantError(e.message)  # noqa: B904
