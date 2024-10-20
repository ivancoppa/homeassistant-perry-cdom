# Perry Electric CDOM for Home Assistant
A custom component designed for Home Assistant with the capability to interact with the Perry Electric Thermostat C.DOM/CRM 4.0.

## Current Status
In the current state the component only reads the data.
It will create a new Climate entity for each zone + 1 for controlling without any temperature.

### What's not working
- Change of temperature
- Power on and off of the thermostats

## Installation

### Manual Installation
Using the tool of choice open the directory (folder) for your HA configuration (where you find configuration.yaml).

If you do not have a custom_components directory (folder) there, you need to create it.

In the custom_components directory (folder) create a new folder called perry_cdom.

Download all the files from the custom_components/perry_cdom/ directory (folder) in this repository.

Place the files you downloaded in the Home Assistant config directory in custom_components/perry_cdom/.

Restart Home Assistant

### Configuration
In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Perry CDOM"

<img src="images/configuration-select-integration.png">

Configure the integration using the following parameters

<img src="images/configuration-configure-thermostat.png">
