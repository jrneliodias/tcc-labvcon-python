from serialApp import serialApp
import time
# portlist = [port.device for port in comports()]
# print(portlist)
# arduinoData = serial.Serial('COM9', 250000)

# time.sleep(1)


# cmd = input('Please Enter Your command: ')
# cmd = cmd + '\n'

# arduinoData.write(cmd.encode())

# while (arduinoData.in_waiting == 0):
#     pass
# dataPacket = arduinoData.readline()
# print(dataPacket)

# Instanciar o objeto
arduino = serialApp()

#  Conectar a porta Serial ex.COM9
arduino.updatePort()
arduino.serialPort.port = arduino.portlist[0]

arduino.serialPort.baudrate = '250000'

arduino.connectSerial()
time.sleep(3)

arduino.readSerial()
print('terminou')
