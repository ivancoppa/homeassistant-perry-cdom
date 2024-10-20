import requests
import json
import logging

_LOGGER = logging.getLogger(__name__)

# api integration for Perry C.DOM 
class PerryCDom():
    def __init__(self, pin, cdom_serial_number) -> None:
        """Init function for the api"""
        _LOGGER.info("API: PerryCDom INIT")
        self.pin = pin
        self.cdom_serial_number = cdom_serial_number

    # Read the stataus of the Thermostat
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
