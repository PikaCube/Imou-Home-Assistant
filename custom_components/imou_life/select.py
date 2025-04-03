import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyimouapi.exceptions import ImouException
from homeassistant.helpers import config_validation as cv, entity_platform
import voluptuous as vol

from .const import (
    DOMAIN,
    PARAM_CURRENT_OPTION,
    PARAM_OPTIONS,
    PARAM_ENTITY_ID,
    SERVICE_SELECT,
    PARAM_OPTION,
)
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
            entities.append(select_entity)
    if len(entities) > 0:
        async_add_entities(entities)

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_SELECT,
        {
            vol.Required(PARAM_ENTITY_ID): cv.entity_id,
            vol.Required(PARAM_OPTION): cv.string,
        },
        "async_select_option",
    )


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
            await self._coordinator.device_manager.async_select_option(
                self._device, self._entity_type, option
            )
            self._device.selects[self._entity_type][PARAM_CURRENT_OPTION] = option
            self.async_write_ha_state()
        except ImouException as e:
            raise HomeAssistantError(e.message)  # noqa: B904
