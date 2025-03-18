import logging

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import ImouEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    _LOGGER.info("ImouBinarySensor.async_setup_entry")
    imou_coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for device in imou_coordinator.devices:
        for binary_sensor_type in device.binary_sensors:
            binary_sensor_entity = ImouBinarySensor(imou_coordinator, entry, binary_sensor_type, device)
            _LOGGER.debug(f"translation_key is {binary_sensor_entity.translation_key},unique_key is {binary_sensor_entity.unique_id}")
            entities.append(binary_sensor_entity)
    if len(entities) > 0:
        async_add_entities(entities)


class ImouBinarySensor(ImouEntity,BinarySensorEntity):
    """imou sensor."""

    @property
    def is_on(self)->bool|None:
        return self._device.binary_sensors[self._entity_type]


    @property
    def device_class(self)->BinarySensorDeviceClass|None:
        match self._entity_type:
            case "door_contact_status":
                return BinarySensorDeviceClass.DOOR
            case _:
                return None
