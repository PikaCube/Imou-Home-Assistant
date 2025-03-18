"""Support for Imou devices."""

import asyncio
import logging
import re

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceEntry
from pyimouapi.const import PARAM_OPERATION, PARAM_DURATION
from pyimouapi.device import ImouDeviceManager
from pyimouapi.ha_device import ImouHaDeviceManager
from pyimouapi.openapi import ImouOpenApiClient

from .const import (
    DOMAIN,
    PARAM_API_URL,
    PARAM_APP_ID,
    PARAM_APP_SECRET,
    PLATFORMS,
    PARAM_UPDATE_INTERVAL,
    SERVICE_CONTROL_MOVE_PTZ,
    PARAM_ENTITY_ID, PARAM_PTZ,
)
from .coordinator import ImouDataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Set up entry."""
    _LOGGER.info("starting setup imou life")
    imou_client = ImouOpenApiClient(
        config.data.get(PARAM_APP_ID),
        config.data.get(PARAM_APP_SECRET),
        config.data.get(PARAM_API_URL),
    )
    device_manager = ImouDeviceManager(imou_client)
    imou_device_manager = ImouHaDeviceManager(device_manager)
    imou_coordinator = ImouDataUpdateCoordinator(
        hass, imou_device_manager, config.options.get(PARAM_UPDATE_INTERVAL, 60)
    )
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config.entry_id] = imou_coordinator
    await imou_coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(config, PLATFORMS)
    config.add_update_listener(async_reload_entry)
    """register service"""
    hass.services.async_register(
        DOMAIN,
        SERVICE_CONTROL_MOVE_PTZ,
        _async_handle_control_move_ptz,
        schema=SERVICE_SCHEMA_CONTROL_MOVE_PTZ,
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    _LOGGER.info("Unloading entry %s", entry.entry_id)
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ],
            # async_remove_devices(hass, entry.entry_id),
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_remove_devices(hass: HomeAssistant, config_entry_id: str):
    """Remove device."""
    device_registry_object = dr.async_get(hass)
    for device_entry in device_registry_object.devices.get_devices_for_config_entry_id(
        config_entry_id
    ):
        _LOGGER.info("remove device %s", device_entry.id)
        device_registry_object.async_remove_device(device_entry.id)
    return True


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry
):
    """Remove device."""
    device_registry_object = dr.async_get(hass)
    device_registry_object.async_remove_device(device_entry.id)
    return True


SERVICE_SCHEMA_CONTROL_MOVE_PTZ = {
    vol.Required(PARAM_ENTITY_ID): cv.string,
    vol.Required(PARAM_DURATION): cv.positive_int,
    vol.Required(PARAM_OPERATION): cv.positive_int,
}


async def _async_handle_control_move_ptz(call):
    """Handle Imou events."""
    hass = call.data.get("hass")
    entity_id = call.data[PARAM_ENTITY_ID]
    operation = call.data[PARAM_OPERATION]
    duration = call.data[PARAM_DURATION]
    registry = await hass.helpers.entity_registry.async_get_registry(hass)
    registry_entry = registry.async_get(entity_id)
    if not registry_entry:
        raise HomeAssistantError(f"Entity {entity_id} not found")
    unique_id = registry_entry.unique_id
    imou_coordinator = hass.data[DOMAIN][registry_entry.config_entry_id]
    device_id = unique_id.split("_")[0]
    channel_id = unique_id.split("_")[1]
    if re.match(r"\d+", channel_id) is None or PARAM_PTZ not in unique_id:
        raise HomeAssistantError(
            f"Invalid channel id {channel_id},device is not a camera"
        )
    await imou_coordinator.device_manager.delegate.async_control_device_ptz(
        device_id, channel_id, operation, duration
    )
