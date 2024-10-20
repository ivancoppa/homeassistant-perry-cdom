from homeassistant import core
from homeassistant.core import HomeAssistant

import logging
import json
from homeassistant.config_entries import ConfigEntry

from . import api

from .const import (
    DOMAIN,
    PLATFORMS,
)

import async_timeout
import asyncio

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Perry CDOM from a config entry."""
    _LOGGER.info("INIT: module init " + config_entry.entry_id)
    _LOGGER.debug("INIT: module init " + json.dumps(dict(config_entry.options)))
    
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True
