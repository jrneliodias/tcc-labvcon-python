from connections import *
import streamlit as st
import pandas as pd

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

if st.button('Conectar Arduino'):
    arduinoData = connectSerialManual(option)
    st.session_state.connected['arduinoData'] = arduinoData

textToSend = st.text_input('Send to Serial:')

if st.button('Enviar'):
    arduinoData = st.session_state.connected['arduinoData']
    actions = ['ON', 'OFF', 'ON', 'OFF']
    for action in actions:
        arduinoData.write(action.encode())
        arduinoData.flush()

        dataRead, *_ = arduinoData.readline().decode().split('\r\n')
    st.write(dataRead)
