import requests
import json
import logging

_LOGGER = logging.getLogger(__name__)

class PerryCDom():
    def __init__(self, pin, cdom_serial_number) -> None:
        """ddsadsdas"""
        _LOGGER.warning("API: PerryCDom INIT")
        self.pin = pin
        self.cdom_serial_number = cdom_serial_number

    def thermoreg_get_info(self):
        url_get = "https://cdom.perryhome.it/CDomWS.svc/rests/ThermoregGetInfo"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "Pin": self.pin,
            "CdomSerialNumber": self.cdom_serial_number
        }
        _LOGGER.warning("API: payload " + json.dumps(payload) ),
        
        response = requests.post(url_get, headers=headers, json=payload)
        _LOGGER.warning("API: PerryCDom response" + str(response.status_code))

        if response.status_code == 200:
            # Step 2: Extract ThermoZonesContainer from response
            data = response.json()
            thermo_zones_container = data.get('ThermoZonesContainer', {})
            print("Original ThermoZonesContainer:")
            print(json.dumps(thermo_zones_container))
            return data
        return {}
