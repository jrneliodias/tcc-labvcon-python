import streamlit as st
import pandas as pd
from formatterInputs import *


def imc_Controller():
    st.header('Controle IMC')

    col1, col2 = st.columns([0.7, 0.3])

    with col1:

        sensor_dict = st.session_state.sensor
        date_object = keys2DatetimeObj(sensor_dict)

        time_interval = [0] + [(date_object[i] - date_object[0]).total_seconds()
                               for i in range(1, len(date_object))]

        sensor_formatted2Hours_dict = {
            key.split()[1]: value
            for key, value in sensor_dict.items()
        }

        new_dict = {time_interval[i]: sensor_dict[key]
                    for i, key in enumerate(sensor_dict)}

        st.line_chart(data=new_dict, height=500)

    with col2:

        tab1, tab2 = st.tabs(["Única Referência", "Múltiplas Referências"])
        with tab1:
            single_2reference = st.number_input(
                'Referência:', value=50, step=1, min_value=0, max_value=90, key='single_reference')
        with tab2:
            col21, col22, col23 = st.columns(3)
            with col21:
                reference = st.number_input(
                    'Referência:', value=50, step=1, min_value=0, max_value=90, key='reference')

            with col22:
                reference2 = st.number_input(
                    'Referência 2:', value=50, step=1, min_value=0, max_value=90,
                    key='reference2')

            with col23:
                reference3 = st.number_input(
                    'Referência 3:', value=50, step=1, min_value=0, max_value=90, key='reference3')
