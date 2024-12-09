###TROUBLESHOOTING
## This code helps to unlock the alicat device
## in the future I will add a structure of controle. CHECK
## I do not know how to include it into tomato but it was very useful
#it is a serial code so maybe it can be used for other devices ??



#in the code :
#ser.write(b'A$$U\r')  # A by default, but when the other part of the code will work we will add a structure of controle for the other channels

import serial
import sys

def check_device_troubles():
    while True:
        print('Do you encounter troubles with your Alicat devices? (yes/no)')
        ans = input('Answer: ').lower()

        if ans == 'yes':
            print('Please enter the port where you encounter troubles with the Alicat device')
            port = input('Port: ')

            try:
                # Attempt to open the serial connection
                ser = serial.Serial(
                    port=port,
                    baudrate=19200,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=2
                )

                try:

                    ser.write(b'A$$U\r')  # 'A' #for now we stick to A, when the other part of the code will work we will add more
                    print(f"Successfully connected to and unlocked device on {port}")
                except Exception as e:
                    print(f"Error communicating with device: {e}")
                finally:
                    ser.close()

                break

            except serial.SerialException as e:
                print(f"Error opening port {port}: {e}")
                print("Please check the port name and try again.")

        elif ans == 'no':
            print("No troubleshooting needed.")
            break

        else:
            print("Invalid input. Please answer 'yes' or 'no'.")

if __name__ == "__main__":
    check_device_troubles()
