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


def connectSerial(commport):

    portlist = get_ports()
    commPort = findArduino(portlist)
    arduinoData = serial.Serial(port=commPort, baudrate=250000, timeout=1)
    time.sleep(6)
    return arduinoData


def connectSerialManual(commPort):

    arduinoData = serial.Serial(port=commPort, baudrate=250000, timeout=1)
    time.sleep(6)
    return arduinoData


def sendToArduino(arduinoData, textToSend):

    arduinoData.write(textToSend.encode())
    arduinoData.flush()
    time.sleep(0.1)
    dataRead = arduinoData.readline().decode().split('\r\n')
    print(dataRead[0])
