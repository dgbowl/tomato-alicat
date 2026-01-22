# tomato-alicat
`tomato` driver for alicat flow and pressure controllers.

This driver is using the serial port interface of Alicat devices, see [Alicat Serial Primer](https://documents.alicat.com/Alicat-Serial-Primer.pdf). This driver is developed by the [ConCat lab at TU Berlin](https://tu.berlin/en/concat).

## Installation
Install the package using `pip`, e.g. `pip install tomato-alicat`. No further driver-specific configuration is necessary.

## Supported functions

### Capabilities
- `constant_flow` for (mass) flow controllers
- `constant_pressure` for pressure controllers

### Attributes
- `setpoint` for all devices; no max/min checks are performed at the moment
- `temperature` for all devices, if available

## Contributors

- Peter Kraus
- Alexandre Gbocho
