"""Config flow."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from homeassistant.components import fan, switch
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN, SensorDeviceClass
from homeassistant.const import CONF_NAME, DEGREE
from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
)
import voluptuous as vol

from .const import (  # CONF_AC_MODE,
    CONF_CDOM_PIN,
    CONF_CDOM_SCAN_INTERVAL,
    CONF_CDOM_SERIAL_NUMBER,
    CONF_COLD_TOLERANCE,
    CONF_HEATER,
    CONF_HOT_TOLERANCE,
    CONF_MIN_DUR,
    CONF_PRESETS,
    CONF_SCAN_INTERVAL_SECONDS,
    CONF_SENSOR,
    DEFAULT_TOLERANCE,
    DOMAIN,
)

OPTIONS_SCHEMA = {
    vol.Required(CONF_CDOM_SERIAL_NUMBER): selector.TextSelector(
        selector.TextSelectorConfig(
            type=selector.TextSelectorType.TEXT,
            autocomplete="CdomSerialNumber",
        )
    ),
    vol.Required(CONF_CDOM_PIN): selector.TextSelector(
        selector.TextSelectorConfig(
            type=selector.TextSelectorType.PASSWORD,
            autocomplete="Pin",
        )
    ),
    vol.Optional(
        CONF_CDOM_SCAN_INTERVAL, default=CONF_SCAN_INTERVAL_SECONDS
    ): selector.NumberSelector(
        selector.NumberSelectorConfig(
            mode=selector.NumberSelectorMode.BOX,
            unit_of_measurement="Seconds",
            step=1,
            min=10,
        )
    ),
}

PRESETS_SCHEMA = {
    vol.Optional(v): selector.NumberSelector(
        selector.NumberSelectorConfig(
            mode=selector.NumberSelectorMode.BOX, unit_of_measurement=DEGREE
        )
    )
    for v in CONF_PRESETS.values()
}

CONFIG_SCHEMA = {
    vol.Required(CONF_NAME): selector.TextSelector(),
    **OPTIONS_SCHEMA,
}

CONFIG_FLOW = {"user": SchemaFlowFormStep(vol.Schema(CONFIG_SCHEMA))}

OPTIONS_FLOW = {"init": SchemaFlowFormStep(vol.Schema(OPTIONS_SCHEMA))}

# CONFIG_FLOW = {
#    "user": SchemaFlowFormStep(vol.Schema(CONFIG_SCHEMA), next_step="presets"),
#    "presets": SchemaFlowFormStep(vol.Schema(PRESETS_SCHEMA)),
# }

# OPTIONS_FLOW = {
#    "init": SchemaFlowFormStep(vol.Schema(OPTIONS_SCHEMA), next_step="presets"),
#    "presets": SchemaFlowFormStep(vol.Schema(PRESETS_SCHEMA)),
# }


class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config or options flow."""

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title."""
        return cast(str, options["name"])
