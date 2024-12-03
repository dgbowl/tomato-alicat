#code to push


import asyncio
import serial.tools.list_ports
from alicat import FlowController
import concurrent.futures

class SynchronousWrapper:
    def __init__(self, async_func):
        self._async_func = async_func
        self._loop = asyncio.new_event_loop()

    def __call__(self, *args, **kwargs):
        return self._loop.run_until_complete(
            self._async_func(*args, **kwargs)
        )

def sync_list_available_ports():
    async def async_list_ports():
        ports = list(serial.tools.list_ports.comports())
        if not ports:
            print("No available serial ports detected.")
            return []
        print("Available Ports:")
        for i, port in enumerate(ports):
            print(f"{i + 1}: {port.device}")
        return [port.device for port in ports]

    return SynchronousWrapper(async_list_ports)()

def sync_flow_controller_operation():
    async def async_flow_controller_operation():
        async with FlowController('COM3', 'A') as flow_controller:
            try:
                # Fetch status
                status = await flow_controller.get()
                print(f"Device Status: {status}")

                # Flow rate setup
                flow_rate = float(input("Enter flow rate (L/min): "))
                await flow_controller.set_flow_rate(flow_rate)
                print(f"Flow rate set to {flow_rate} L/min.")

                # Pressure setup
                pressure = float(input("Enter pressure (bar): "))
                await flow_controller.set_pressure(pressure)
                print(f"Pressure set to {pressure} bar.")

                # Gas type setup
                gas_type = input("Enter gas type (N2/O2/CO2/Ar): ")
                await flow_controller.set_gas(gas_type)
                print(f"Gas set to {gas_type}.")

            except Exception as e:
                print(f"An error occurred: {e}")

    return SynchronousWrapper(async_flow_controller_operation)()

def main():
    # List available ports synchronously
    ports = sync_list_available_ports()

    if not ports:
        print("No ports available.")
        return

    # Select port
    while True:
        try:
            port_selection = int(input("Select port number: "))
            if 1 <= port_selection <= len(ports):
                selected_port = ports[port_selection - 1]
                print(f"Selected port: {selected_port}")
                break
            else:
                print("Invalid port selection.")
        except ValueError:
            print("Please enter a valid number.")

    # Perform flow controller operation
    sync_flow_controller_operation()

if __name__ == "__main__":
    main()
