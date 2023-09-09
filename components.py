from connections import *
import streamlit as st
import pandas as pd
import datetime


def sidebarMenu():
    st.write('#### Componentes Seriais Encontrados:')

    portlist = get_ports()
    for port_info in portlist:
        st.write(
            f"Description: {port_info.description}")

    port_option = st.selectbox(
        'Qual porta deseja conectar?',
        [port_info.device for port_info in portlist])

    col11, col12 = st.columns(2)
    with col11:
        if st.button('Conectar'):
            serialPortValidationToConnect(port_option)

    with col12:
        if st.button('Desconectar'):
            serialPortValidationToDisconnect()

    textToSend = st.text_input('Send to Serial:')

    if st.button('Enviar'):
        if 'arduinoData' in st.session_state.connected:
            arduinoData = st.session_state.connected['arduinoData']
            sendToArduino(arduinoData, textToSend)
            dataRead = readFromArduino(arduinoData, 0.1)
            st.write(dataRead)
        else:
            st.warning('Não há dispositivos conectados.')

    if st.button('Receber Dados'):
        if 'arduinoData' in st.session_state.connected:
            arduinoData = st.session_state.connected['arduinoData']
            st.session_state.sensor = dict()
            sensor = st.session_state.sensor
            for i in range(800):
                sendToArduino(arduinoData, 'ON')
                dataRead = readFromArduino(arduinoData, 0)
                current_timestamp = datetime.datetime.now()
                sensor[str(current_timestamp)] = float(dataRead)
            st.write(dataRead)
        else:
            st.warning('Não há dispositivos conectados.')
