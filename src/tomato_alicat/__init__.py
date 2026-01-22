from typing import Any
from threading import RLock
from tomato.driverinterface_2_1 import ModelInterface, ModelDevice, Attr
from tomato.driverinterface_2_1.decorators import coerce_val
from tomato.driverinterface_2_1.types import Val
from datetime import datetime
import xarray as xr
import pint
import time
from functools import wraps
import serial
import logging

pint.set_application_registry(pint.UnitRegistry(autoconvert_offset_to_baseunit=True))
logger = logging.getLogger(__name__)

UNIT_MAP = {
    "SCCM": "ml/min",
    "mbarA": "mbar",
}

PARAM_MAP = {
    "f_setpoint": 37,
    "p_setpoint": 34,
    "pressure": 2,
    "flow": 5,
}


READ_DELAY = 0.02
SERIAL_TIMEOUT = 0.2
READ_TIMEOUT = 2.0
QUERY_INTERVAL = 1.0


def read_delay(func):
    @wraps(func)
    def wrapper(self: ModelDevice, **kwargs):
        if time.perf_counter() - self.last_action < READ_DELAY:
            time.sleep(READ_DELAY)
        return func(self, **kwargs)

    return wrapper


class DriverInterface(ModelInterface):
    idle_measurement_interval = 10.0
    portlock: RLock
    smap: dict[str, serial.Serial]

    def __init__(self, settings=None):
        super().__init__(settings)
        self.portlock = RLock()
        self.smap = dict()

    def DeviceFactory(self, key, **kwargs):
        return Device(self, key, **kwargs)


class Device(ModelDevice):
    s: serial.Serial
    """:class:`serial.Serial` port, used for communication with the device."""

    portlock: RLock
    """:class:`threading.RLock`, used to ensure exclusive access to the serial port"""

    last_action: float
    """a timestamp of last MODBUS read/write obtained using :func:`time.perf_counter`"""

    last_query: float

    portid: str

    device_type: str

    device_unit: str

    device_setpoint: int

    _temperature: pint.Quantity

    _setpoint: pint.Quantity

    _fmeasure: pint.Quantity

    def __init__(self, driver: ModelInterface, key: tuple[str, str], **kwargs: dict):
        address, self.portid = key
        self.portlock = driver.portlock
        if address not in driver.smap:
            try:
                driver.smap[address] = serial.Serial(
                    port=address,
                    baudrate=19200,
                    bytesize=8,
                    parity="N",
                    stopbits=1,
                    exclusive=True,
                    timeout=SERIAL_TIMEOUT,
                )
            except serial.SerialException as e:
                logger.error(e, exc_info=True)
                raise RuntimeError(str(e)) from e

        self.s = driver.smap[address]

        info = self._comm(f"{self.portid}??M*\r".encode())
        if "Model Number MCS-" in info:
            self.device_type = "flow"
            self.device_setpoint = PARAM_MAP["f_setpoint"]
        elif "Model Number PC-" in info:
            self.device_type = "pressure"
            self.device_setpoint = PARAM_MAP["p_setpoint"]
        logger.debug("device_type = %s", self.device_type)

        setp_unit = self._comm(f"{self.portid}DCU {self.device_setpoint}\r".encode())
        self.device_unit = UNIT_MAP[setp_unit.split()[-1]]
        logger.debug("device_unit = %s", self.device_unit)

        self.last_query = 0
        super().__init__(driver, key, **kwargs)

    def attrs(self, **kwargs) -> dict[str, Attr]:
        """
        Returns a dict of available attributes for the device, depending on its type (PC or MFC).
        """

        attrs_dict = {
            "setpoint": Attr(
                type=pint.Quantity,
                units=self.device_unit,
                status=True,
                rw=True,
            ),
        }
        if self.device_type == "flow":
            attrs_dict["temperature"] = Attr(
                type=pint.Quantity,
                units="celsius",
                status=False,
            )

        return attrs_dict

    @coerce_val
    def set_attr(self, attr: str, val: Any, **kwargs: dict) -> Val:
        if isinstance(val, pint.Quantity):
            props = self.attrs()[attr]
            ret = self._comm(f"{self.portid}S {val.to(props.units).m}\r".encode())
        else:
            ret = self._comm(f"{self.portid}S {val}\r".encode())
        items = ret.split()
        idx = 2 if self.device_type == "pressure" else 5
        return pint.Quantity(f"{items[idx]} {self.device_unit}")

    def get_attr(self, attr: str, **kwargs: dict) -> Val:
        if time.perf_counter() - self.last_query > QUERY_INTERVAL:
            ret = self._comm(f"{self.portid}\r".encode())
            items = ret.split()
            idx = 2 if self.device_type == "pressure" else 5
            self._setpoint = pint.Quantity(f"{items[idx]} {self.device_unit}")
            idx = 1 if self.device_type == "pressure" else 4
            self._fmeasure = pint.Quantity(f"{items[idx]} {self.device_unit}")
            if "temperature" in self.attrs():
                self._temperature = pint.Quantity(f"{items[2]} degC")
            self.last_query = time.perf_counter()
        if attr not in self.attrs():
            raise AttributeError(f"unknown attr: {attr!r}")
        return getattr(self, f"_{attr}")

    def capabilities(self, **kwargs) -> set:
        if self.device_type == "pressure":
            caps = {"constant_pressure"}
        else:
            caps = {"constant_flow"}
        return caps

    def do_measure(self, **kwargs):
        data_vars = {}
        for key, props in self.attrs(**kwargs).items():
            val = self.get_attr(attr=key)
            if props.units is not None:
                data_vars[key] = (["uts"], [val.m], {"units": str(val.u)})
            else:
                data_vars[key] = (["uts"], [val])
        if self.device_type == "pressure":
            data_vars["pressure"] = (
                ["uts"],
                [self._fmeasure.m],
                {"units": str(self._fmeasure.u)},
            )
        else:
            data_vars["flow"] = (
                ["uts"],
                [self._fmeasure.m],
                {"units": str(self._fmeasure.u)},
            )
        self.last_data = xr.Dataset(
            data_vars=data_vars,
            coords={"uts": (["uts"], [datetime.now().timestamp()])},
        )

    def _comm(self, command: bytes) -> list[str]:
        lines = []
        t0 = time.perf_counter()
        with self.portlock:
            logger.debug("%s", command.rstrip())
            self.s.write(command)
            while time.perf_counter() - t0 < READ_TIMEOUT:
                lines += self.s.readlines()
                logger.debug("%s", lines)
                if len(lines) > 0:
                    break
                time.sleep(READ_DELAY)
            else:
                raise RuntimeError(f"Read took too long: {lines}")
        lines = [i.decode().strip() for i in lines]
        logger.debug("comm = %s", lines)
        return "\n".join(lines)
