from connections import *
from components import *
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",

)

if 'connected' not in st.session_state:
    st.session_state.connected = {}

if 'sensor' not in st.session_state:
    st.session_state.sensor = {}

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
