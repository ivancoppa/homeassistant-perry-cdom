from homeassistant import core
import logging

from .const import (
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

#async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
#    """Set up the Perry CDOM component."""
#    # @TODO: Add setup code.
#    return True



#async def async_setup(hass: HomeAssistant, config: dict):
async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the component from configuration.yaml."""
    hass.data.setdefault(DOMAIN, {})

    if hass.config_entries.async_entries(DOMAIN):
        return True
    _LOGGER.warning("Testing module")

#    if DOMAIN in config:
#        _LOGGER.info("Found existing  configuration.")
#        hass.async_create_task(
#            hass.config_entries.flow.async_init(
#                DOMAIN,
#                context={"source": SOURCE_IMPORT},
#                data=config[DOMAIN],
#            )
#        )

    return True
