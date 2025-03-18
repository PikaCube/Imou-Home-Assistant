"""An abstract class common to all IMOU entities."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pyimouapi.ha_device import DeviceStatus, ImouHaDevice

from . import ImouDataUpdateCoordinator
from .const import DOMAIN, PARAM_STATUS

_LOGGER: logging.Logger = logging.getLogger(__package__)


class ImouEntity(CoordinatorEntity):
    """EntityBaseClass."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ImouDataUpdateCoordinator,
        config_entry: ConfigEntry,
        entity_type: str,
        device: ImouHaDevice,
    ) -> None:
        """Init ImouEntity."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.config_entry = config_entry
        self._entity_type = entity_type
        self._device = device
        self.entity_available = None

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # The combination of DeviceId and ChannelId uniquely identifies the device
                (
                    DOMAIN,
                    self._device.device_id + "_" + self._device.channel_id
                    if self._device.channel_id is not None
                    else self._device.product_id,
                )
            },
            name=self._device.channel_name
            if self._device.channel_name is not None
            else self._device.device_name,
            manufacturer=self._device.manufacturer,
            model=self._device.model,
            sw_version=self._device.swversion,
            serial_number=self._device.device_id,
        )

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        unique_id = f"{self._device.device_id}_{self._device.channel_id if self._device.channel_id is not None else self._device.product_id}${self._entity_type}"
        _LOGGER.debug(f"device_id is {self._device.device_id}")
        _LOGGER.debug(f"unique_id is {unique_id}")
        _LOGGER.debug(f"_entity_type is {self._entity_type}")
        return unique_id

    @property
    def translation_key(self):
        """Return translation_key."""
        return self._entity_type

    @property
    def available(self) -> bool:
        """Return entity is available."""
        if self._entity_type == PARAM_STATUS:
            return True
        return self._device.sensors[PARAM_STATUS] != DeviceStatus.OFFLINE.value
