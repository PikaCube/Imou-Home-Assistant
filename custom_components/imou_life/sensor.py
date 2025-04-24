import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyimouapi.const import PARAM_STATE

from .const import DOMAIN
from .entity import ImouEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    _LOGGER.info("ImouSensor.async_setup_entry")
    imou_coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for device in imou_coordinator.devices:
        for sensor_type, value in device.sensors.items():
            sensor_entity = ImouSensor(imou_coordinator, entry, sensor_type, device)
            entities.append(sensor_entity)
    if len(entities) > 0:
        async_add_entities(entities)


class ImouSensor(ImouEntity, SensorEntity):
    """imou sensor."""

    @property
    def native_value(self):
        return self._device.sensors[self._entity_type][PARAM_STATE]

    @property
    def native_unit_of_measurement(self) -> str | None:
        match self._entity_type:
            case "battery":
                return "%"
            case "storage_used":
                if self.is_non_negative_number(self.native_value):
                    return "%"
                return None
            case "temperature_current":
                return "°C"
            case "humidity_current":
                return "%RH"
            case _:
                return None

    @property
    def device_class(self) -> SensorDeviceClass | None:
        match self._entity_type:
            case "battery":
                return SensorDeviceClass.BATTERY
            case "temperature_current":
                return SensorDeviceClass.TEMPERATURE
            case "humidity_current":
                return SensorDeviceClass.HUMIDITY
            case _:
                return None

    @property
    def suggested_display_precision(self) -> int | None:
        match self._entity_type:
            case "battery":
                return 0
            case "temperature_current":
                return 1
            case "humidity_current":
                return 1
            case "storage_used":
                return 0
            case _:
                return None
