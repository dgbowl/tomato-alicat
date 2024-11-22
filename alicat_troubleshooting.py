###TROUBLESHOOTING
## This code helps to unlock the alicat device
## in the future I will add a structure of controle.
## I do not know how to include it into tomato but it was very useful
#it is a serial code so maybe it can be used for other devices ??
import serial


#it is a very simple code, in the future I will add a structure of controle
ser = serial.Serial(
    port='COM3',
    baudrate=19200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE
)

# unlocking the device
ser.write(b'A$$U\r')  # 'A' is default Unit ID
ser.close()