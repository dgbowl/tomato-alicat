from tomato_alicat import DriverInterface, Device
import time

kwargsA = dict(address="COM15", channel="A")
kwargsB = dict(address="COM15", channel="B")
interface = DriverInterface()
print(f"{interface=}")
print(f"{interface.cmp_register(**kwargsA)=}")
print(f"{interface.cmp_register(**kwargsB)=}")
print(f"{interface.cmp_get_attr(attr='setpoint', **kwargsA)=}")
print(f"{interface.cmp_get_attr(attr='setpoint', **kwargsB)=}")
print(f"{interface.cmp_get_attr(attr='temperature', **kwargsA)=}")

time.sleep(1)
print(f"{interface.cmp_set_attr(attr='setpoint', val=5.0, **kwargsA)=}")
print(f"{interface.cmp_set_attr(attr='setpoint', val=1750.0, **kwargsB)=}")

print(f"{interface.cmp_measure(**kwargsA)=}")
print(f"{interface.cmp_measure(**kwargsB)=}")

for t in range(10):
    time.sleep(10)
    print(f"{interface.cmp_last_data(**kwargsA)=}")
    print(f"{interface.cmp_last_data(**kwargsB)=}")
