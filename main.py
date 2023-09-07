from connections import *
import streamlit as st
import pandas as pd


def readFromArduino(arduinoData, ts):
    time.sleep(ts)
    dataRead, *_ = arduinoData.readline().decode().split('\r\n')
    st.write(dataRead)
    return dataRead


st.write('### Componentes Seriais conectados:')

portlist = get_ports()
for port_info in portlist:
    st.write(
        f"Device: {port_info.device}, Description: {port_info.description}")


option = st.selectbox(
    '## Qual porta deseja conectar?',
    [port_info.device for port_info in portlist])

'You selected: ', option

if 'connected' not in st.session_state:
    st.session_state.connected = {}

col1, col2 = st.columns(2)

with col1:
    if st.button('Conectar Arduino'):
        if 'arduinoData' not in st.session_state.connected:
            arduinoData = connectSerialManual(option)
            st.session_state.connected['arduinoData'] = arduinoData
        else:
            st.write('O arduino já está conectado.')


with col2:
    if st.button('Desconectar Arduino'):
        if 'arduinoData' in st.session_state.connected:
            arduinoData = st.session_state.connected['arduinoData']
            disconnectSerial(arduinoData)
            st.session_state.connected = {}
        else:
            st.write('O arduino está desconectado.')


textToSend = st.text_input('Send to Serial:')

if st.button('Enviar'):
    arduinoData = st.session_state.connected['arduinoData']
    sendToArduino(arduinoData, textToSend)
    readFromArduino(arduinoData, 0.1)

st.session_state
