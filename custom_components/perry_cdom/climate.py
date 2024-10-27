"""Support for Perry CDOM Smart thermostats."""

from __future__ import annotations

from datetime import timedelta
import json
import logging
from typing import Any

from homeassistant.components.climate import (
    PRESET_AWAY,
    PRESET_BOOST,
    PRESET_COMFORT,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CDOM_SHARED_SEASON_WINTER,
    CDOM_SHARED_THERMO_MODE_OFF,
    CONF_UPDATE_INTERVAL_SECONDS,
    DOMAIN,
    PRESET_FROST_GUARD,
    PRESET_MANAGED,
)

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import PerryCDomApiClient

CURRENT_HVAC_MAP = {True: HVACAction.HEATING, False: HVACAction.IDLE}


_LOGGER = logging.getLogger(__name__)
# Time between updating data from GitHub
SCAN_INTERVAL = timedelta(seconds=CONF_UPDATE_INTERVAL_SECONDS)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Climate platform."""
    _LOGGER.info("CLIMATE: Set up the Climate platform. Id: " + config.entry_id)
    _LOGGER.debug(
        "CLIMATE: Set up the Climate platform. Config Options: "
        + json.dumps(dict(config.options))
    )

    unit = hass.config.units.temperature_unit
    ac_mode = False
    initial_hvac_mode = HVACMode.AUTO

    unique_id = "perry_cdom"

    # hub = PerryCdomCrm4API(async_get_clientsession(hass), dict(config.options)["cdom_serial_number"], dict(config.options)["cdom_pin"])

    client = PerryCDomApiClient(
        async_get_clientsession(hass),
        dict(config.options)["cdom_serial_number"],
        dict(config.options)["cdom_pin"],
    )
    await client.async_get_thermostat()

    coordinator = PerryCoordinator(
        hass,
        client=client,
        update_interval=timedelta(seconds=config.options["cdom_scan_interval"]),
    )

    await coordinator.update()

    thermozone = coordinator.get_thermozone()
    _LOGGER.debug(
        "CLIMATE: Set up the Climate platform. Config Options: "
        + json.dumps(thermozone)
    )

    entities = []
    controller = PerryCdomThermostat(
        config.options["name"]
        + " - Controller",  # "Perry C.DOM/CRM4.0" + str(thermozone['CdomSerialNumber']),
        True,
        ac_mode,
        initial_hvac_mode,
        unit,
        unique_id + "_" + str(thermozone["CdomSerialNumber"]) + "_controller",
        0,
        coordinator,
    )
    controller.update_data(thermozone, None)
    entities.append(controller)

    for zone in thermozone["zones"]:
        thermostat = PerryCdomThermostat(
            config.options["name"] + " - " + zone["name"],
            False,
            ac_mode,
            initial_hvac_mode,
            unit,
            unique_id
            + "_"
            + str(thermozone["CdomSerialNumber"])
            + "_"
            + str(zone["name"]),
            zone["zoneId"],
            coordinator,
        )
        thermostat.update_data(thermozone, zone)
        entities.append(thermostat)

    async_add_entities(entities)


class PerryCdomThermostat(ClimateEntity, RestoreEntity):
    """Representation of a Perry C.Dom Thermostat device."""

    def __init__(
        self,
        # hub: PerryCdomCrm4API,
        name: str | None,
        controller: bool | None,
        ac_mode: bool | None,
        initial_hvac_mode: HVACMode | None,
        unit: UnitOfTemperature,
        unique_id: str | None,
        zone_id: int | None,
        coordinator,
    ) -> None:
        self.platforms = []
        self.data = dict()
        self.thermozone = dict()
        self.zones = dict()

        self.ac_mode = ac_mode
        self.controller = controller
        self.thermo_type = "valve"
        if self.controller:
            self.thermo_type = "controller"
        self._zone_id = zone_id
        # self._hvac_mode = initial_hvac_mode
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._attr_temperature_unit = unit

        if self.ac_mode:
            self._attr_hvac_modes = [HVACMode.AUTO, HVACMode.OFF]
        else:
            self._attr_hvac_modes = [HVACMode.AUTO, HVACMode.OFF]

        _LOGGER.info(
            "CLIMATE: PerryCdomThermostat INIT UID: "
            + self._attr_unique_id
            + " Name: "
            + self._attr_name
            + " - zone "
            + str(self._zone_id)
        )

        self._coordinator = coordinator
        self._attr_hvac_mode = HVACMode.AUTO

        if controller:
            self._attr_preset_mode = PRESET_MANAGED
            self._attr_preset_modes = [PRESET_MANAGED, PRESET_AWAY, PRESET_BOOST]
            self._attr_supported_features = (
                ClimateEntityFeature.TURN_OFF
                | ClimateEntityFeature.TURN_ON
                | ClimateEntityFeature.PRESET_MODE
            )
        else:
            self._attr_supported_features = (
                ClimateEntityFeature.TARGET_TEMPERATURE
                | ClimateEntityFeature.TURN_OFF
                | ClimateEntityFeature.TURN_ON
            )

    def async_update_callback(self) -> None:
        """Call Back"""
        _LOGGER.debug("CLIMATE: PerryCoordinator async_update_callback ")

    def _update_data(self):
        """Internal update"""
        _LOGGER.warning("PerryCoordinator _update_data " + json.dumps(self.zones))
        self.update_data(self.thermozone, self.zones[self._zone_id])

    def update_data(self, thermozone, zone: None):
        """Update self data"""

        # if season is not winter set cool mode
        self.season = thermozone["currentSeason"]
        if self.season == CDOM_SHARED_SEASON_WINTER:
            self._attr_hvac_modes = [HVACMode.AUTO, HVACMode.OFF]
        else:
            self._attr_hvac_modes = [HVACMode.AUTO, HVACMode.OFF]

        if self.controller or zone is None:
            # Update the data only if it's the coordinator
            self.current_thermo_mode = thermozone["currentSharedThermoMode"]
            if self.current_thermo_mode == CDOM_SHARED_THERMO_MODE_OFF:
                self._attr_hvac_mode = HVACMode.OFF
                self._attr_preset_mode = PRESET_AWAY
            else:
                self._attr_hvac_mode = HVACMode.AUTO
                self._attr_preset_mode = PRESET_MANAGED

            action = HVACAction.IDLE
            temperature = 100
            for zone in thermozone["zones"]:
                target_temperature = 0
                match zone["currentProfileLevel"]:
                    case 1:
                        target_temperature = zone["functionsParams"]["winterT1SetPoint"]
                    case 2:
                        target_temperature = zone["functionsParams"]["winterT2SetPoint"]
                    case 3:
                        target_temperature = thermozone["t3SetPointWinter"]
                    case 5:
                        target_temperature = zone["customTemperatureForManualMode"]
                if target_temperature > zone["lastTemperature"]:
                    action = HVACAction.HEATING
                    break
                else:
                    action = HVACAction.IDLE

                if zone["lastTemperature"] < temperature:
                    temperature = zone["lastTemperature"]

            self._attr_current_temperature = temperature
            self._attr_hvac_action = action

        else:
            _LOGGER.debug(
                f"PerryCoordinator update_data: set mode {zone['currentMode']} and temperature {self._attr_target_temperature}"
            )
            if zone["currentMode"] == 2 and self._attr_target_temperature == 5:
                self._attr_hvac_mode = HVACMode.OFF
            else:
                self._attr_hvac_mode = HVACMode.AUTO

            self._attr_current_temperature = zone["lastTemperature"]

            self.open_valve = zone["temperatureDevice"]["openValve"]
            # if zone['temperatureDevice']['openValve'] == False and zone['askingComfortTemperature'] == False:
            #    self._attr_hvac_mode = HVACMode.AUTO
            # else:
            #    self._attr_hvac_mode = HVACMode.OFF
            if zone["currentMode"] == 2 and zone["currentProfileLevel"] == 5:
                self._attr_hvac_mode = HVACMode.HEAT
                self._attr_hvac_modes = [HVACMode.AUTO, HVACMode.HEAT, HVACMode.OFF]
            else:
                self._attr_hvac_modes = [HVACMode.AUTO, HVACMode.OFF]

            self._attr_max_temp = thermozone["maxTemperatureThreshold"]
            self._attr_min_temp = thermozone["minTemperatureThreshold"]

            if zone["humidity"] > 0:
                self._attr_current_humidity = zone["humidity"]
            match zone["currentProfileLevel"]:
                case 1:
                    self._attr_target_temperature = zone["functionsParams"][
                        "winterT1SetPoint"
                    ]
                case 2:
                    self._attr_target_temperature = zone["functionsParams"][
                        "winterT2SetPoint"
                    ]
                case 3:
                    self._attr_target_temperature = thermozone["t3SetPointWinter"]
                case 5:
                    self._attr_target_temperature = zone[
                        "customTemperatureForManualMode"
                    ]

            if self._attr_target_temperature > self._attr_current_temperature:
                self._attr_hvac_action = HVACAction.HEATING
            else:
                self._attr_hvac_action = HVACAction.IDLE

    async def async_update(self) -> None:
        """Async Update"""
        _LOGGER.debug(
            "CLIMATE: PerryCoordinator async_update id " + self._attr_unique_id
        )
        data = self._coordinator.get_zone(self._zone_id)
        rawdata = self._coordinator.get_thermozone()
        # _LOGGER.info("CLIMATE: PerryCoordinator async_update data: " + json.dumps(data))
        # _LOGGER.info("CLIMATE: PerryCoordinator async_update rawdata: " + json.dumps(rawdata))

        self.update_data(rawdata, data)

    async def async_added_to_hass(self):
        """async_added_to_hass"""
        _LOGGER.debug("CLIMATE: PerryCoordinator async_added_to_hass ")
        await super().async_added_to_hass()
        self._coordinator.async_add_listener(self.async_write_ha_state)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        _LOGGER.info(f"PerryCoordinator async_set_hvac_mode {hvac_mode}")
        if hvac_mode == HVACMode.OFF:
            await self.async_turn_off()
        elif hvac_mode in (HVACMode.AUTO, HVACMode.HEAT):
            await self.async_turn_heat()

        self.hass.async_create_task(self.async_update(), eager_start=True)
        self.async_write_ha_state()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        _LOGGER.info("PerryCoordinator async_set_preset_mode " + preset_mode)
        if preset_mode in (PRESET_BOOST):
            _LOGGER.info("PerryCoordinator async_set_preset_mode set all temp to max")
            for zone in self.zones:
                await self._coordinator.set_temperature_manual(30)

        if preset_mode in (PRESET_AWAY, PRESET_FROST_GUARD):
            _LOGGER.info(
                "PerryCoordinator async_set_preset_mode set thermoregulation off"
            )
            await self._coordinator.set_thermoregulation_off()

        if preset_mode in (PRESET_COMFORT, PRESET_MANAGED):
            _LOGGER.info(
                "PerryCoordinator async_set_preset_mode set all temp to default"
            )
            await self._coordinator.set_thermoregulation_on()
            for zone in self.zones:
                await self._coordinator.set_temperature_auto()

        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        _LOGGER.info("PerryCoordinator async_turn_off")
        if self.thermo_type == "controller":
            await self._coordinator.set_thermoregulation_off()
        if self.thermo_type == "valve":
            await self._coordinator.set_zone_temperature_manual(self._zone_id, 5)

        self.hass.async_create_task(self.async_update(), eager_start=True)
        self.async_write_ha_state()

    async def async_turn_heat(self) -> None:
        """Turn the entity heat."""
        _LOGGER.info("PerryCoordinator async_turn_off")
        if self.thermo_type == "controller":
            await self._coordinator.set_thermoregulation_on()
        if self.thermo_type == "valve":
            await self._coordinator.set_zone_temperature_auto(self._zone_id)

        self.hass.async_create_task(self.async_update(), eager_start=True)
        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature for 2 hours."""
        _LOGGER.info("PerryCoordinator async_set_temperature " + str(self._zone_id))
        _LOGGER.info("PerryCoordinator async_set_temperature " + json.dumps(kwargs))
        if self.thermo_type == "valve":
            await self._coordinator.set_zone_temperature_manual(
                self._zone_id, kwargs["temperature"]
            )
            self.hass.async_create_task(self.async_update(), eager_start=True)
        self.async_write_ha_state()


class PerryCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: PerryCDomApiClient,
        update_interval: timedelta,
    ):
        self.hass = hass
        self.perry_api = client
        self.platforms = []
        self.data = dict()
        self.thermozone = dict()
        self.zones = dict()
        self.report_last_updated = None

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    def get_data(self):
        _LOGGER.debug("PerryCoordinator get_data: data")
        try:
            _LOGGER.debug("PerryCoordinator get_data: data " + json.dumps(self.data))
            return self.data
        except Exception as error:
            _LOGGER.info(f"An error occured while getting data: {error}")
            return False

    def get_thermozone(self):
        return self.perry_api.get_thermozone()

    def get_zone(self, zone_id):
        # _LOGGER.warning("PerryCoordinator get_data: data " + json.dumps(self.data) )
        _LOGGER.debug("PerryCoordinator get_data: zone")
        try:
            return self.zones[zone_id]
        except Exception as error:
            _LOGGER.info(
                f"An error occured while getting zone using zone_id {str(zone_id)}: {error}"
            )
            return False

    async def _async_update_data(self):
        """Update data via library."""
        _LOGGER.debug("Updating data from Perry CDOM: _async_update_data")
        await self.update()

    async def update(self) -> bool:
        """Update status from Perry CDOM"""
        _LOGGER.info("API: PerryCDom update " + str(type(self.perry_api.thermostat)))
        await self.perry_api.async_get_thermostat()

        self.zones[0] = dict()
        for zone in self.perry_api.get_thermozone()["zones"]:
            self.zones[zone["zoneId"]] = zone
        return True
        # # Update data
        # _LOGGER.info("Updating data from Perry CDOM")

        # try:
        #     _LOGGER.warning("Updating data from Perry CDOM api object")

        #     # get data from api
        #     perrydata = await self.perry_api.async_get_thermostat()
        #     _LOGGER.warning("PerryCoordinator NEW LIB update: result " + str(type(perrydata)) )
        #     _LOGGER.warning("PerryCoordinator NEW LIB update: result " + json.dumps(dict(perrydata.initial_data)) )
        #     self.data = perrydata.initial_data

        #     self.thermozone = self.data['ThermoZonesContainer']
        #     self.zones[0]=dict()
        #     for zone in self.data['ThermoZonesContainer']['zones']:
        #         self.zones[zone['zoneId']] = zone
        #     _LOGGER.info("PerryCoordinator update: result " + json.dumps(self.data) )
        #     _LOGGER.debug("PerryCoordinator update: result " + json.dumps(self.zones) )
        #     return True
        # except Exception as error:
        #     _LOGGER.warning(f"An error occured while requesting update from Perry CDOM: {error}")
        #     return False

    async def set_thermoregulation_on(self) -> bool:
        return await self.perry_api.set_thermoregulation_on()

    async def set_thermoregulation_off(self) -> bool:
        return await self.perry_api.set_thermoregulation_off()

    async def set_zone_temperature_manual(self, zone_id, temperature) -> bool:
        return await self.perry_api.set_zone_temperature_manual(zone_id, temperature)

    async def set_zone_temperature_auto(self, zone_id) -> bool:
        return await self.perry_api.set_zone_temperature_auto(zone_id)

    async def set_temperature_manual(self, zone_id, temperature) -> bool:
        return await self.perry_api.set_temperature_manual(temperature)

    async def set_temperature_auto(self, zone_id) -> bool:
        return await self.perry_api.set_temperature_auto()
