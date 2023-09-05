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

if st.button('Conectar Arduino'):
    connectSerialManual(option)
