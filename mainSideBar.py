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
