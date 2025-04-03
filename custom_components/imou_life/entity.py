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
        self._coordinator = coordinator
        self._config_entry = config_entry
        self._entity_type = entity_type
        self._device = device

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # The combination of DeviceId and ChannelId uniquely identifies the device
                (
                    DOMAIN,
                    f"{self._device.device_id}_{self._device.channel_id or self._device.product_id}",
                )
            },
            name=self._device.channel_name or self._device.device_name,
            manufacturer=self._device.manufacturer,
            model=self._device.model,
            sw_version=self._device.swversion,
            serial_number=self._device.device_id,
        )

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        unique_id = f"{self._device.device_id}_{self._device.channel_id or self._device.product_id}${self._entity_type}"
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

    @staticmethod
    def is_non_negative_number(s):
        try:
            # 尝试将字符串转换为浮点数
            number = float(s)
            # 判断是否大于等于0
            return number >= 0
        except ValueError:
            # 如果转换失败，说明字符串不是有效的数字
            return False
