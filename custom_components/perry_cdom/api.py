import requests
import json
import logging

_LOGGER = logging.getLogger(__name__)

SHARED_THERMO_MODE_ON = 0
SHARED_THERMO_MODE_OFF = 5

# api integration for Perry C.DOM 
class PerryCDom():
    def __init__(self, pin, cdom_serial_number) -> None:
        """Init function for the api"""
        _LOGGER.info("API: PerryCDom INIT")
        self.pin = pin
        self.cdom_serial_number = cdom_serial_number

    # Read the status of the Thermostat
    def thermoreg_get_info(self):
        url_get = "https://cdom.perryhome.it/CDomWS.svc/rests/ThermoregGetInfo"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "Pin": self.pin,
            "CdomSerialNumber": self.cdom_serial_number
        }
        _LOGGER.debug("API: payload " + json.dumps(payload) ),
        
        response = requests.post(url_get, headers=headers, json=payload)
        _LOGGER.debug("API: PerryCDom response" + str(response.status_code))

        if response.status_code == 200:
            # Step 2: Extract ThermoZonesContainer from response
            data = response.json()
            return data
        return {}
    
    # Write the status of the Thermostat
    def _thermoreg_set_working_mode(self, thermo_zone_container):
        url_get = "https://cdom.perryhome.it/CDomWS.svc/rests/ThermoregSetWorkingMode"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "Pin": self.pin,
            "CdomSerialNumber": self.cdom_serial_number,
            "ThermoZonesContainer": json.dumps(thermo_zone_container) # The modified zones container
        }
        _LOGGER.info("API: payload " + json.dumps(payload) ),
        
        response = requests.post(url_get, headers=headers, json=payload)
        _LOGGER.info("API: PerryCDom response" + str(response.status_code))

        if response.status_code == 200:
            # Step 2: Extract ThermoZonesContainer from response
            data = response.json()
            _LOGGER.info("API: PerryCDom response" + json.dumps(data))
            return data
        return {}
    
    def set_working_mode(self, mode):
        payload = {}
        payload['currentSharedThermoMode'] = mode,
        return self._thermoreg_set_working_mode(payload)

    def set_thermoregulation(self, thermo_zone_container):
        payload = thermo_zone_container
        if isinstance(payload, list):
            payload = thermo_zone_container[0]
        del payload['CdomSerialNumber']
        del payload['CreationDate']
        del payload['easyModeCoolingActivationTime']
        del payload['easyModeCoolingSwitchOffTime']
        del payload['easyModeHeatingActivationTime']
        del payload['easyModeHeatingSwitchOffTime']
        _LOGGER.info("API: set_thermoregulation " + json.dumps(payload) )
        return self._thermoreg_set_working_mode(payload)
