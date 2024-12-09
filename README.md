# tomato-alicat
`tomato` driver for alicat flow and pressure controllers.

This driver is a wrapper around the [`numat-alicat`]https://github.com/numat/alicat library. This driver is developed by the [ConCat lab at TU Berlin](https://tu.berlin/en/concat).

## Supported functions

### Capabilities 
- `constant_flow` for (mass) flow controllers 
-  `get_gas_type` for (mass) flow controllers and pressure controllers


### Attributes
- `flow` for flow controllers
- `setpoint` for all devices, within the capacity range
- `temperature` for all devices, if available

## Contributors

- Peter Kraus
- Alexandre Gbocho
