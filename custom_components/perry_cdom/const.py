DOMAIN = "perry_cdom"


"""Constants for the Generic Thermostat helper."""

from homeassistant.components.climate import (
    PRESET_ACTIVITY,
    PRESET_AWAY,
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_HOME,
    PRESET_SLEEP,
)
from homeassistant.const import Platform

PLATFORMS = [Platform.CLIMATE]


CONF_CDOM_SERIAL_NUMBER = "cdom_serial_number"
CONF_CDOM_PIN = "cdom_pin"
CONF_CDOM_SCAN_INTERVAL = "cdom_scan_interval"
CONF_SCAN_INTERVAL_SECONDS = 10

CONF_AC_MODE = "ac_mode"
CONF_COLD_TOLERANCE = "cold_tolerance"
CONF_HEATER = "heater"
CONF_HOT_TOLERANCE = "hot_tolerance"
CONF_MIN_DUR = "min_cycle_duration"
CONF_PRESETS = {
    p: f"{p}_temp"
    for p in (
        PRESET_AWAY,
        PRESET_COMFORT,
        PRESET_ECO,
        PRESET_HOME,
        PRESET_SLEEP,
        PRESET_ACTIVITY,
    )
}
CONF_SENSOR = "target_sensor"
DEFAULT_TOLERANCE = 0.3