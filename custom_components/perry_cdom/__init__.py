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
    """Set up Netatmo from a config entry."""
    _LOGGER.warning("INIT: Testing module init")
    _LOGGER.warning("INIT: Testing module init " + config_entry.entry_id)
    _LOGGER.warning("INIT: Testing module init " + json.dumps(dict(config_entry.options)))

#    banana = api.PerryCDom(dict(config_entry.options)["cdom_pin"],dict(config_entry.options)["cdom_serial_number"])
    #loop = asyncio.get_running_loop()
#
    #result = await loop.run_in_executor(None, banana.thermoreg_get_info)

    #_LOGGER.warning("INIT API: result " + json.dumps(result) ),


    # try:
    #     # Note: asyncio.TimeoutError and aiohttp.ClientError are already
    #     # handled by the data update coordinator.
    #     async with async_timeout.timeout(10):
    #         # Grab active context variables to limit data required to be fetched from API
    #         # Note: using context is not required if there is no need or ability to limit
    #         # data retrieved from API.
    #         return await banana.thermoreg_get_info()

    # except:
    #     _LOGGER.warning("INIT: Testing module init")



    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


#async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
#    """Set up the Perry CDOM component."""
#    # @TODO: Add setup code.
#    return True



#async def async_setup(hass: HomeAssistant, config: dict):
#async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
#    """Set up the component from configuration.yaml."""
#    hass.data.setdefault(DOMAIN, {})

#    if hass.config_entries.async_entries(DOMAIN):
#        return True
#    _LOGGER.warning("Testing module")

#    if DOMAIN in config:
#        _LOGGER.info("Found existing  configuration.")
#        hass.async_create_task(
#            hass.config_entries.flow.async_init(
#                DOMAIN,
#                context={"source": SOURCE_IMPORT},
#                data=config[DOMAIN],
#            )
#        )

#    return True
