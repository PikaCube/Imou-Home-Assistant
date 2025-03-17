"""Imou camera entity."""

import logging
import re

from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyimouapi.exceptions import ImouException
from pyimouapi.ha_device import ImouHaDevice

from . import ImouDataUpdateCoordinator
from .const import DOMAIN, PARAM_MOTION_DETECT, PARAM_STORAGE_USED, PARAM_LIVE_RESOLUTION, PARAM_LIVE_PROTOCOL, \
    PARAM_DOWNLOAD_SNAP_WAIT_TIME, PARAM_HEADER_DETECT
from .entity import ImouEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(  # noqa: D103
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    imou_coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for device in imou_coordinator.devices:
        if device.channel_id is not None:
            camera_entity = ImouCamera(imou_coordinator, entry,"camera", device)
            entities.append(camera_entity)
    if len(entities) > 0:
        async_add_entities(entities)


class ImouCamera(ImouEntity, Camera):
    """imou camera."""

    _attr_supported_features = CameraEntityFeature.STREAM

    def __init__(self, coordinator: ImouDataUpdateCoordinator, config_entry: ConfigEntry, entity_type: str,device: ImouHaDevice):
        Camera.__init__(self)
        ImouEntity.__init__(coordinator, config_entry, entity_type, device)
        self._attr_name = entity_type

    async def stream_source(self) -> str | None:
        """GET STREAMING ADDRESS."""
        try:
            return await self.coordinator.device_manager.async_get_device_stream(
                self._device,self.config_entry.options.get(PARAM_LIVE_RESOLUTION),self.config_entry.options.get(PARAM_LIVE_PROTOCOL),
            )
        except ImouException as e:
            raise HomeAssistantError(e.message)  # noqa: B904

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return bytes of camera image."""
        try:
            return await self.coordinator.device_manager.async_get_device_image(
                self._device,self.config_entry.options.get(PARAM_DOWNLOAD_SNAP_WAIT_TIME)
            )
        except ImouException as e:
            raise HomeAssistantError(e.message)  # noqa: B904

    @property
    def is_recording(self) -> bool:
        """The battery level is normal and the motion detect is activated, indicating that it is in  recording mode."""
        return (
                self.is_strict_number(self._device.sensors[PARAM_STORAGE_USED] if PARAM_STORAGE_USED in self._device.sensors else "")
                and (
                    self._device.switches[PARAM_HEADER_DETECT] if PARAM_HEADER_DETECT in self._device.switches else False
                    or
                    self._device.switches[PARAM_MOTION_DETECT] if PARAM_MOTION_DETECT in self._device.switches else False
                )
        )

    @property
    def is_streaming(self) -> bool:  # noqa: D102
        if self.stream is None:
            return False
        return self.stream._thread is not None and self.stream._thread.is_alive()  # noqa: SLF001

    @property
    def motion_detection_enabled(self) -> bool:
        """Camera Motion Detection Status."""
        return (self._device.switches[PARAM_MOTION_DETECT] if PARAM_MOTION_DETECT in self._device.switches else False
                or
                self._device.switches[PARAM_HEADER_DETECT] if PARAM_HEADER_DETECT in self._device.switches else False)

    @staticmethod
    def is_strict_number(s):
        return re.match(r"^-?\d+(\.\d+)?$", s) is not None