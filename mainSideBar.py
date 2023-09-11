from connections import *
import streamlit as st
import pandas as pd
import datetime


def mainSidebarMenu():
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

    col1, col2 = st.columns(2)
    with col1:
        sampling_time_input = st.number_input(
            'Tempo de amostragem:',
            value=0.1,
            min_value=0.005)
        if sampling_time_input:
            st.session_state.sampling_time = sampling_time_input

    with col2:

        samples_number = st.number_input(
            'Quantidade de amostras:', value=100, step=10, min_value=1)

        if samples_number:
            st.session_state.samples_number = samples_number

    if st.button('Receber Dados'):
        enviarDados('ON')


def enviarDados(controlSignal: str = '0,0'):
    if 'sensor' not in st.session_state:
        return st.error('Não há dispositivos conectados.')

    # Receber o objeto arduino da sessão
    arduinoData = st.session_state.connected['arduinoData']

    # limpar os valores anteriores do sensor
    st.session_state.sensor = dict()
    sensor = st.session_state.sensor

    # inicializar  o timer
    start_time = time.time()
    interation = 0

    # Receber os valores de tempo de amostragem e número de amostras da sessão
    sampling_time = st.session_state.sampling_time
    samples_number = st.session_state.samples_number

    # Inicializar a barra de progresso
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)

    while interation < samples_number:
        current_time = time.time()
        if current_time - start_time > sampling_time:
            start_time = current_time
            sendToArduino(arduinoData, controlSignal)
            dataRead = readFromArduino(arduinoData)
            current_timestamp = datetime.datetime.now()
            sensor[str(current_timestamp)] = float(dataRead)
            interation += 1

            percent_complete = interation * 1 / samples_number
            my_bar.progress(percent_complete, text=progress_text)
