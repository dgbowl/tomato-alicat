import serial.tools.list_ports
from functools import wraps
from alicat import FlowController

#code to push on github , not testedyet 

#here we try to convert asynchronos to synchronous using the wrap function
#I need to try it in the lab
# @sync_wrap decorator to maintain similar function signatures it should work ?
#
#NO TESTED :
def sync_wrap(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def list_available_ports():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No available serial ports detected.")
        return []
    print("Available Ports:")
    for i, port in enumerate(ports):
        print(f"{i + 1}: {port.device}")
    return [port.device for port in ports]


def get_flow_rate():
    while True:
        try:
            flow_rate = float(input("Enter the flow rate (L/min): "))
            if not (0.1 <= flow_rate <= 5.0):
                raise ValueError("Flow rate must be between 0.1 and 5.0 L/min.")
            return flow_rate
        except ValueError as e:
            print(f"Invalid input: {e}")


def get_pressure():
    while True:
        try:
            pressure = float(input("Enter the pressure (bar): "))
            if not (0 <= pressure <= 100):
                raise ValueError("Pressure must be between 0 and 100 bar.")
            return pressure
        except ValueError as e:
            print(f"Invalid input: {e}")


def get_gas_type():
    allowed_gases = ['N2', 'O2', 'CO2', 'Ar']
    while True:
        gas = input("Enter the gas type (e.g., N2, O2, CO2, Ar): ").strip()
        if gas in allowed_gases:
            return gas
        print(f"Invalid gas type. Allowed gases are: {', '.join(allowed_gases)}.")


def ask_tare_pressure():
    while True:
        tare_response = input("Do you want to tare the pressure? (yes/no): ").strip().lower()
        if tare_response in ['yes', 'no']:
            return tare_response == 'yes'
        print("Invalid input. Please answer with 'yes' or 'no'.")


def ask_tare_volumetric_flow():
    while True:
        tare_response = input("Do you want to tare the volumetric flow? (yes/no): ").strip().lower()
        if tare_response in ['yes', 'no']:
            return tare_response == 'yes'
        print("Invalid input. Please answer with 'yes' or 'no'.")


@sync_wrap
def detect_device(flow_controller):
    try:
        device_info = flow_controller.identify()
        print(f"Connected to device: {device_info}")
        return device_info
    except Exception as e:
        print(f"Failed to detect the device. Error: {e}")
        raise


def main():
    # List ports
    ports = list_available_ports()
    if not ports:
        return

    while True:
        try:
            port_selection = int(input("Select the port number (e.g., 1, 2): "))
            if 1 <= port_selection <= len(ports):
                selected_port = ports[port_selection - 1]
                print(f"Selected port: {selected_port}")
                break
            else:
                raise ValueError("Invalid port number.")
        except (ValueError, IndexError):
            print("Invalid selection. Please try again.")

    # Run the main experiment control
    with FlowController(selected_port, 'A') as flow_controller:
        try:
            # Detect device
            device_info = detect_device(flow_controller)
            print(f"Device detected: {device_info}")

            # Fetch and configure flow rate
            flow_rate = get_flow_rate()
            flow_controller.set_flow_rate(flow_rate)
            print(f"Flow rate set to {flow_rate} L/min.")

            # Fetch and configure pressure
            pressure = get_pressure()
            flow_controller.set_pressure(pressure)
            print(f"Pressure set to {pressure} bar.")

            # Configure gas type
            gas = get_gas_type()
            flow_controller.set_gas(gas)
            print(f"Gas set to {gas}.")

            # Tare options
            if ask_tare_pressure():
                flow_controller.tare_pressure()
                print("Pressure tared.")
            if ask_tare_volumetric_flow():
                flow_controller.tare_volumetric()
                print("Volumetric flow tared.")

        except Exception as e:
            print(f"An error occurred during communication with the device: {e}")


if __name__ == "__main__":
    main()
