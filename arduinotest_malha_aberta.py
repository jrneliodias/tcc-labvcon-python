import time
import serial
from serial.tools.list_ports import comports
import numpy as np
import matplotlib.pyplot as plt

portlist = [port.device for port in comports()]
print(portlist)

arduinoData = serial.Serial(port=portlist[0], baudrate=250000, timeout=1)

time.sleep(6)


reference = 50*np.ones(30)
temperature = np.zeros(30)

for i in range(30):
    cmd = str(reference[i])
    cmd += '\r'
    arduinoData.write(cmd.encode())
    arduinoData.flush()
    time.sleep(1)
    dataRead = arduinoData.readline().decode().split('\r\n')

    temperature[i] = float(dataRead[0])

cmd = '0\r'
arduinoData.write(cmd.encode())

time_interval = np.arange(0,30,1)

plt.figure(1)
plt.plot(time_interval, temperature,label='Resposta do sistema')
plt.legend()
plt.xlabel('Tempo (s)')
plt.ylabel('Temperatura (º)')
plt.title('Resposta do Sistema')

plt.show()
