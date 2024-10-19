"""Support for Netatmo Smart thermostats."""

from __future__ import annotations

import logging
from typing import Any, cast
from datetime import timedelta
from . import api
import asyncio
import json

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, VolDictType
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)

from homeassistant.components.climate import (
    ATTR_PRESET_MODE,
    PLATFORM_SCHEMA as CLIMATE_PLATFORM_SCHEMA,
    PRESET_NONE,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)

from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_TEMPERATURE,
    CONF_NAME,
    CONF_UNIQUE_ID,
    EVENT_HOMEASSISTANT_START,
    PRECISION_HALVES,
    PRECISION_TENTHS,
    PRECISION_WHOLE,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_ON,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfTemperature,
)

from .const import (
    DOMAIN,
    PLATFORMS,
    CONF_SCAN_INTERVAL_SECONDS
)


_LOGGER = logging.getLogger(__name__)
# Time between updating data from GitHub
SCAN_INTERVAL = timedelta(seconds=CONF_SCAN_INTERVAL_SECONDS)

async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Climate platform."""
    _LOGGER.warning("CLIMATE: Testing module climate")
    _LOGGER.warning("CLIMATE: Testing module climate " + config.entry_id)

    unit = hass.config.units.temperature_unit
    ac_mode = False
    initial_hvac_mode = HVACMode.AUTO
 
    unique_id = "perrycdom"

    coordinator = PerryCoordinator(hass, config,SCAN_INTERVAL)
    await coordinator.update()

    thermozone = coordinator.get_thermozone()

    entities = []
    for zone in thermozone['zones']:
        thermostat = TestThermostat(
            zone['name'],
            ac_mode,
            initial_hvac_mode,
            unit,
            unique_id + '_' + str(thermozone['CdomSerialNumber']) + '_' + str(zone['zoneId']),
            zone['zoneId'],
            coordinator
        )
        thermostat.update_data(thermozone, zone)
        entities.append(
            thermostat
        )

    async_add_entities(entities)

    
async def async_update(self) -> None:
    """dsds"""
    _LOGGER.warning("CLIMATE: CLIMATE async_update ")



class TestThermostat(ClimateEntity, RestoreEntity):
    """Representation of a Generic Thermostat device."""

    def __init__(
        self,
        name: str | None,
        ac_mode: bool | None,
        initial_hvac_mode: HVACMode | None,
        unit: UnitOfTemperature,
        unique_id: str | None,
        zone_id: int | None,
        coordinator,
        ) -> None:
        """ddsadsdas"""
        _LOGGER.warning("CLIMATE: GenericThermostat INIT")


    # _attr_current_humidity: int | None = None
    # _attr_current_temperature: float | None = None
    # _attr_fan_mode: str | None
    # _attr_fan_modes: list[str] | None
    # _attr_hvac_action: HVACAction | None = None
    # _attr_hvac_mode: HVACMode | None
    # _attr_hvac_modes: list[HVACMode]
    # _attr_is_aux_heat: bool | None
    # _attr_max_humidity: float = DEFAULT_MAX_HUMIDITY
    # _attr_max_temp: float
    # _attr_min_humidity: float = DEFAULT_MIN_HUMIDITY
    # _attr_min_temp: float
    # _attr_precision: float
    # _attr_preset_mode: str | None
    # _attr_preset_modes: list[str] | None
    # _attr_supported_features: ClimateEntityFeature = ClimateEntityFeature(0)
    # _attr_swing_mode: str | None
    # _attr_swing_modes: list[str] | None
    # _attr_target_humidity: float | None = None
    # _attr_target_temperature_high: float | None
    # _attr_target_temperature_low: float | None
    # _attr_target_temperature_step: float | None = None
    # _attr_target_temperature: float | None = None
    # _attr_temperature_unit: str

        self.ac_mode = ac_mode
        self._hvac_mode = initial_hvac_mode
        self._attr_name = name
        self._attr_hvac_mode = initial_hvac_mode

        if self.ac_mode:
            self._attr_hvac_modes = [HVACMode.COOL, HVACMode.OFF]
        else:
            self._attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]

        self._attr_unique_id = unique_id

        self._attr_temperature_unit = unit
        self._cur_temp = 18
        self._min_temp = 5
        self._max_temp = 39
        self._target_temp = 25
        self._attr_current_temperature = 18
        self._attr_preset_mode = PRESET_NONE
        self._zone_id = zone_id

        self._coordinator=coordinator

        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        )

    def async_update_callback(self) -> None:
        """dsds"""
        _LOGGER.warning("CLIMATE: GenericThermostat async_update_callback ")

    def update_data(self, thermozone, zone):
        """Update self data"""
        self._attr_current_temperature=zone['lastTemperature']
        self.open_valve=zone['temperatureDevice']['openValve']
        if zone['temperatureDevice']['openValve'] == False and zone['askingComfortTemperature'] == False:
            self._attr_hvac_mode = HVACMode.OFF
        else:
            self._attr_hvac_mode = HVACMode.HEAT

        self._attr_max_temp = thermozone['maxTemperatureThreshold']
        self._attr_min_temp = thermozone['minTemperatureThreshold']

        if zone['humidity'] > 0:
            self._attr_current_humidity = zone['humidity']
        match zone['currentProfileLevel']:
            case 1:
                self._attr_target_temperature = zone['functionsParams']['winterT1SetPoint']
            case 2:
                self._attr_target_temperature = zone['functionsParams']['winterT2SetPoint']
            case 3:
                self._attr_target_temperature = thermozone['t3SetPointWinter']
            case 5:
                self._attr_target_temperature = zone['customTemperatureForManualMode']




    async def async_update(self) -> None:
        """dsds"""
        _LOGGER.warning("CLIMATE: GenericThermostat async_update ")
        data = self._coordinator.get_zone(self._zone_id)
        rawdata = self._coordinator.get_thermozone()
        self.update_data(rawdata,data)


    async def async_added_to_hass(self):
        """dsds"""
        _LOGGER.warning("CLIMATE: GenericThermostat async_added_to_hass ")
        await super().async_added_to_hass()
        self._coordinator.async_add_listener(self.async_write_ha_state)


class PerryCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, entry, update_interval: timedelta):
        self.hass = hass
        self.entry = entry
        self.platforms = []
        self.data = dict()
        self.thermozone = dict()
        self.zones = dict()
        self.report_last_updated = None

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    def get_data(self):
        _LOGGER.warning("PerryCoordinator get_data: data")
        try:
            _LOGGER.debug("PerryCoordinator get_data: data " + json.dumps(self.data) )
            return(self.data)
        except Exception as error:
            _LOGGER.warning(f"An error occured while getting data: {error}")
            return False
        
    def get_thermozone(self):
        _LOGGER.warning("PerryCoordinator get_data: data")
        try:
            _LOGGER.debug("PerryCoordinator get_data: data " + json.dumps(self.data) )
            return(self.thermozone)
        except Exception as error:
            _LOGGER.warning(f"An error occured while getting thermozone: {error}")
            return False

    def get_zone(self,zone_id):
        #_LOGGER.warning("PerryCoordinator get_data: data " + json.dumps(self.data) )
        _LOGGER.warning("PerryCoordinator get_data: zone")
        try:
            return(self.zones[zone_id])
        except Exception as error:
            _LOGGER.debug(f"An error occured while getting zone using zone_id " + zone_id +  ": {error}")
            return False


    async def _async_update_data(self):
        """Update data via library."""
        _LOGGER.warning("Updating data from Perry CDOM: _async_update_data")
        await self.update()
        #_LOGGER.warning("PerryCoordinator _async_update_data: data " + json.dumps(self.data) )

    async def update(self) -> bool:
        """Update status from Perry CDOM"""

        # Update vehicle data
        _LOGGER.warning("Updating data from Perry CDOM")
        try:
            _LOGGER.warning("GET DATA")
            banana = api.PerryCDom(dict(self.entry.options)["cdom_pin"],dict(self.entry.options)["cdom_serial_number"])
            loop = asyncio.get_running_loop()

            data = await loop.run_in_executor(None, banana.thermoreg_get_info)
            self.data = data
            self.thermozone = self.data['ThermoZonesContainer']
            for zone in self.data['ThermoZonesContainer']['zones']:
                self.zones[zone['zoneId']] = zone
            _LOGGER.debug("PerryCoordinator update: result " + json.dumps(self.data) )
            _LOGGER.debug("PerryCoordinator update: result " + json.dumps(self.zones) )
            return True
        except Exception as error:
            _LOGGER.warning(f"An error occured while requesting update from Perry CDOM: {error}")
            return False
            
