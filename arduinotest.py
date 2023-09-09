import time
import serial
from serial.tools.list_ports import comports

portlist = [port.device for port in comports()]
print(portlist)
arduinoData = serial.Serial(port=portlist[0], baudrate=250000, timeout=1)

time.sleep(6)


def createInput():
    cmd = input('Please Enter Your command: ')
    cmd = + '\r'
    return cmd


for i in range(5):
    actions = ['ON', 'OFF', 'ON', 'OFF']
    arduinoData.write(actions[i].encode())
    arduinoData.flush()
    time.sleep(0.1)
    dataRead = arduinoData.readline().decode().split('\r\n')

    print(dataRead[0])
