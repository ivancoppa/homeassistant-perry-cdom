import asyncio
import json
import logging

import async_timeout
from homeassistant import core
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import api
from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Perry CDOM from a config entry."""
    _LOGGER.info("INIT: module init " + config_entry.entry_id)
    _LOGGER.debug("INIT: module init " + json.dumps(dict(config_entry.options)))

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True
