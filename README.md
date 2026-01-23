# tomato-alicat
`tomato` driver for alicat flow and pressure controllers.

This driver is using the serial port interface of Alicat devices, see [Alicat Serial Primer](https://documents.alicat.com/Alicat-Serial-Primer.pdf). This driver is developed by the [ConCat lab at TU Berlin](https://tu.berlin/en/concat).

## Installation
Install the package using `pip`, e.g. `pip install tomato-alicat`. No further driver-specific configuration is necessary.

## Supported functions

### Capabilities
- `constant_flow` for mass flow controllers (model number starts with `MCS-`)
- `constant_pressure` for pressure controllers (model number starts with `PC-`)

### Attributes
- `setpoint` of the controller, for all devices, `pint.Quantity(float, self.device_unit)`
- `temperature` of the controller if available, `pint.Quantity(float, "celsius")`
- `valve_close` indicating whether the valve is shut, `bool`

## Contributors

- Peter Kraus
- Alexandre Gbocho
