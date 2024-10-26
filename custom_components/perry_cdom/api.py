import logging


from aiohttp import ClientSession
from perry_cdom_api_community.api import PerryCdomCrm4API
from perry_cdom_api_community.entity import PerryThermostat

SHARED_THERMO_MODE_ON = 0
SHARED_THERMO_MODE_OFF = 5

_LOGGER = logging.getLogger(__name__)


# api integration for Perry C.DOM
class PerryCDomApiClient:
    def __init__(
        self, session: ClientSession, cdom_serial_number: str, cdom_pin: int
    ) -> None:
        """Init function for the api"""
        self.cdom_serial_number = cdom_serial_number
        self.cdom_pin = cdom_pin
        _LOGGER.info("API: PerryCDom INIT")
        api = PerryCdomCrm4API(session, self.cdom_serial_number, self.cdom_pin)
        self.thermostat = PerryThermostat(self.cdom_serial_number, api)
        # await self.thermostat.get_thermostat()

    # Read the status of the Thermostat
    async def async_get_thermostat(self) -> PerryThermostat:
        _LOGGER.info("API: PerryCDom get Data " + str(type(self.thermostat)))
        await self.thermostat.get_thermostat()
        return self.thermostat

    def get_thermostat(self):
        return self.thermostat

    def get_thermozone(self):
        return self.thermostat.get_data()["ThermoZonesContainer"]

    async def set_thermoregulation_on(self) -> bool:
        await self.thermostat.set_thermoregulation_on()
        return True

    async def set_thermoregulation_off(self) -> bool:
        await self.thermostat.set_thermoregulation_off()
        return True

    async def set_zone_temperature_manual(self, zone_id, temperature) -> bool:
        await self.thermostat.set_zone_temperature_manual(zone_id, temperature)
        return True

    async def set_zone_temperature_auto(self, zone_id) -> bool:
        await self.thermostat.set_zone_temperature_auto(zone_id)
        return True
