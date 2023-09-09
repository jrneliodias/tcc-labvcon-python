from connections import *
from components import *
from session_state import *
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",

)

st.header('LABVCON - Laboratório Virtual de Controle', divider='rainbow')
selectMethod = option_menu(
    menu_title=None,
    options=['PID', 'IMC', 'GMV', 'GPC'],
    orientation='horizontal',
    icons=['diagram-2', 'ui-radios-grid',
           'app', 'command'],

)


# SideBar
with st.sidebar:
    sidebarMenu()
    st.session_state

st.line_chart(data=st.session_state.sensor)


col1, col2 = st.columns(2)

with col1:

    datetimeList = list(st.session_state.sensor.keys())

    # Define the format of your date string
    date_format = "%Y-%m-%d %H:%M:%S.%f"

    # Parse the string into a datetime object
    date_object = [datetime.strptime(datetimeElement, date_format)
                   for datetimeElement in datetimeList]

    time_interval = [(date_object[i] - date_object[i-1]).total_seconds()
                     for i in range(1, len(date_object))]

    st.line_chart(time_interval)

with col2:

    if time_interval:
        'Média do intervalo'
        mean_value = sum(time_interval) / len(time_interval)
        mean_value
        'Média do erro'
        mean_error = sum(abs(x - mean_value)
                         for x in time_interval) / len(time_interval)
        mean_error/0.0001

    'Tempo da simulação'
    if date_object:
        date_object[-1] - date_object[0]
