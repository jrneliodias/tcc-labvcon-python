import time
import serial
from serial.tools.list_ports import comports
import streamlit as st


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


def disconnectSerial(arduinoData):
    arduinoData.close


def sendToArduino(arduinoData, textToSend):
    if '\r' not in textToSend:
        textToSend += '\r'
    arduinoData.write(textToSend.encode())
    arduinoData.flush()


def readFromArduino(arduinoData):
    ts = st.session_state.sampling_time
    time.sleep(ts)
    dataRead, *_ = arduinoData.readline().decode().split('\r\n')
    return dataRead


def serialPortValidationToConnect(port_option):
    if not port_option:
        return st.error('Não há porta serial para conectar')

    if 'arduinoData' not in st.session_state.connected:
        with st.spinner('Processing...'):
            arduinoData = connectSerialManual(port_option)
            st.session_state.connected['arduinoData'] = arduinoData
        st.success("Conectado!")
    else:
        st.write('O arduino já está conectado.')


def serialPortValidationToDisconnect():
    if 'arduinoData' in st.session_state.connected:
        arduinoData = st.session_state.connected['arduinoData']
        with st.spinner('Processing...'):
            time.sleep(2)
            disconnectSerial(arduinoData)
            st.session_state.connected = {}
        st.success("Desconectado!")
    else:
        st.warning('O arduino já está desconectado.')
