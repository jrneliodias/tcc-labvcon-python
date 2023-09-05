import time
import serial
from serial.tools.list_ports import comports


def get_ports():
    portlist = comports()
    return portlist


def findArduino(portsFound: list):
    commPort = ''

    for port in portsFound:
        if 'Arduino' in str(port):
            commPort = port.device
    return commPort


def connectSerial():

    portlist = get_ports()
    commPort = findArduino(portlist)
    arduinoData = serial.Serial(port=commPort, baudrate=250000, timeout=1)
    time.sleep(6)
    return arduinoData


connectSerial()
