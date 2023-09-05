from serialApp import serialApp
import time

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
