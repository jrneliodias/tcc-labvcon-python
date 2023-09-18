import streamlit as st


def loadSessionStates():
    if 'connected' not in st.session_state:
        st.session_state.connected = {}

    if 'sensor' not in st.session_state:
        st.session_state.sensor = {}

    if 'controller_parameters' not in st.session_state:
        st.session_state.controller_parameters = {}

    if 'sampling_time' not in st.session_state.controller_parameters:
        st.session_state.controller_parameters['sampling_time'] = 0.1

    if 'samples_number' not in st.session_state.controller_parameters:
        st.session_state.controller_parameters['samples_number'] = 100

    if 'angle_reference' not in st.session_state.controller_parameters:
        st.session_state.controller_parameters['angle_reference'] = {}

    if 'control_signal_1' not in st.session_state.controller_parameters:
        st.session_state.controller_parameters['control_signal_1'] = {}

    if 'control_signal_2' not in st.session_state.controller_parameters:
        st.session_state.controller_parameters['control_signal_2'] = {}
