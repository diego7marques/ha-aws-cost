"""The AWS Cost integration."""

from __future__ import annotations
import logging

from .const import DOMAIN
from .coordinator import AWSCostDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Set up the AWS Cost component."""
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass, config_entry):
    """Set up AWS Cost from a config entry."""
    # Store coordinator in hass.data for the sensor platform to use
    coordinator = AWSCostDataUpdateCoordinator(hass, config_entry)
    hass.data[DOMAIN][config_entry.entry_id] = coordinator
    
    # Forward setup to sensor platform
    await hass.config_entries.async_forward_entry_setups(config_entry, ["sensor"])

    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    # Unload sensor platform
    unload_ok = await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
    
    # Clean up coordinator from hass.data
    if config_entry.entry_id in hass.data[DOMAIN]:
        del hass.data[DOMAIN][config_entry.entry_id]

    return unload_ok
