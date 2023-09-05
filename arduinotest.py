import time
import serial
from serial.tools.list_ports import comports

portlist = [port.device for port in comports()]
print(portlist)
arduinoData = serial.Serial(port=portlist[0], baudrate=250000, timeout=1)

time.sleep(6)

for i in range(5):
    cmd = input('Please Enter Your command: ')
    if cmd == "q":
        break
    cmd = cmd + '\r'
    arduinoData.write(cmd.encode())
    arduinoData.flush()
    time.sleep(0.1)
    dataRead = arduinoData.readline().decode().split('\r\n')

    print(dataRead[0])
