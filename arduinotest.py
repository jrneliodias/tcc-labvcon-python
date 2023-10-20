import time
import serial
from serial.tools.list_ports import comports
import numpy as np

portlist = [port.device for port in comports()]
print(portlist)

arduinoData = serial.Serial(port=portlist[0], baudrate=250000, timeout=1)

time.sleep(6)


reference = 50*np.ones(30)

for i in range(5):
    cmd = input('Please Enter Your command: ')
    cmd += '\r'
    arduinoData.write(cmd.encode())
    arduinoData.flush()
    time.sleep(0.1)
    dataRead = arduinoData.readline().decode().split('\r\n')

    print(dataRead[0])
