#CODE to push on github



import asyncio
from alicat import FlowController, FlowMeter
from aioconsole import ainput
import serial.tools.list_ports




#for this code, we keep everything asynchronous ... to communicate with the device in a simple way
# hopefully we will find a way to bypass the asynchronous code soon....
# part 1 : here we focus mainly on the MFC
## part 2 with the pc coming (soon) ?


#this little function is better than what we had with bronkhorst.
async def list_available_ports():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No available serial ports detected.")
        return []
    print("Available Ports:")
    for i, port in enumerate(ports):
        print(f"{i + 1}: {port.device}")
    return [port.device for port in ports]


#On Monday
#TO MODIFY : get the units from the device
#there is a modification (it works but these are not the unit of the device... )

async def get_flow_rate():
    while True:
        try:
            flow_rate = float(await ainput("Enter the flow rate (L/min): "))
            if not (0.1 <= flow_rate <= 5.0):
                raise ValueError("Flow rate must be between 0.1 and 5.0 L/min.")
            return flow_rate
        except ValueError as e:
            print(f"Invalid input: {e}")


#tested, depend on the mode we are using

async def get_pressure():
    while True:
        try:
            pressure = float(await ainput("Enter the pressure (bar): "))
            if not (0 <= pressure <= 100):
                raise ValueError("Pressure must be between 0 and 100 bar.")
            return pressure
        except ValueError as e:
            print(f"Invalid input: {e}")

#to test :
#normally the device already have a list of gas supported in the
# alicat --help
#so maybe this get_gas_type is useless and will be removed. if not ? then I will update it

async def get_gas_type():
    allowed_gases = ['N2', 'O2', 'CO2', 'Ar']
    while True:
        gas = (await ainput("Enter the gas type (e.g., N2, O2, CO2, Ar): ")).strip()
        if gas in allowed_gases:
            return gas
        print(f"Invalid gas type. Allowed gases are: {', '.join(allowed_gases)}.")


async def ask_tare_pressure():
    while True:
        tare_response = (await ainput("Do you want to tare the pressure? (yes/no): ")).strip().lower()
        if tare_response in ['yes', 'no']:
            return tare_response == 'yes'
        print("Invalid input. Please answer with 'yes' or 'no'.")


async def ask_tare_volumetric_flow():
    while True:
        tare_response = (await ainput("Do you want to tare the volumetric flow? (yes/no): ")).strip().lower()  # Ensure `await` is used
        if tare_response in ['yes', 'no']:
            return tare_response == 'yes'
        print("Invalid input. Please answer with 'yes' or 'no'.")



#I will have to modify the async FlowController('input of the user', 'channel enter by the user')
# Next week
async def get():
    async with FlowController('COM3', 'A') as flow_controller:
        try:
            print("Fetching current device status...")
            status = await flow_controller.get()
            print(f"Device Status: {status}")

            # Flow rate setup
            flow_rate = await get_flow_rate()
            await flow_controller.set_flow_rate(flow_rate)
            print(f"Flow rate set to {flow_rate} L/min.")

            # Pressure setup
            pressure = await get_pressure()
            await flow_controller.set_pressure(pressure)
            print(f"Pressure set to {pressure} bar.")

            # Gas type setup
            gas = await get_gas_type()
            await flow_controller.set_gas(gas)
            print(f"Gas set to {gas}.")

            # Ask if user wants to tare the pressure
            if await ask_tare_pressure():
                print("Taring pressure...")
                await flow_controller.tare_pressure()
                print("Pressure tared.")
            else:
                print("Skipping tare pressure.")

            # Ask if user wants to tare the volumetric flow
            if await ask_tare_volumetric_flow():
                print("Taring volumetric flow...")
                await flow_controller.tare_volumetric()
                print("Volumetric flow tared.")
            else:
                print("Skipping tare volumetric flow.")

        except Exception as e:
            print(f"An error occurred during communication with the device: {e}")

# Asynchronous entry point
async def main():
    # List ports asynchronously
    ports = await list_available_ports()
    if not ports:
        return


    while True:
        try:
            port_selection = int(await ainput("Select the port number (e.g., 1, 2): "))
            if 1 <= port_selection <= len(ports):
                selected_port = ports[port_selection - 1]
                print(f"Selected port: {selected_port}")
                break
            else:
                raise ValueError("Invalid port number.")
        except (ValueError, IndexError):
            print("Invalid selection. Please try again.")

    # Run the main experiment control
    await get()

# Run the asyncio loop
asyncio.run(main())

### to complete on monday
##Switching mode and recognize the device .

## --------------------------------### I will complete this function on monday
## the goal is to be able to switch the mode when you launch the code
## you should be (will be) able to determine the mode you wanna have
## eventually print something that proves you are currently using a certain mode.

## Beside this I am also currently searching how to determine what kind of the device we are working with
##incoming
#async def switch_modes(device):
    # Switch to Mass Flow control mode
 #   await device.set_control_point('flow')
  #  print("Switched to Mass Flow control mode")

    # Switch to Volumetric Flow control mode
    #await device.set_control_point('volumetric_flow')
    #print("Switched to Volumetric Flow control mode")

    # Switch to Pressure control mode
    #await device.set_control_point('pressure')
    #print("Switched to Pressure control mode")

#async def main():
 #   async with FlowController('COM3', 'A') as device:
  #      await switch_modes(device)

#asyncio.run(main())