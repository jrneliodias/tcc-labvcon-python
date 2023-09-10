import streamlit as st


def loadSessionStates():
    if 'connected' not in st.session_state:
        st.session_state.connected = {}

    if 'sensor' not in st.session_state:
        st.session_state.sensor = {}

    if 'sampling_time' not in st.session_state:
        st.session_state.sampling_time = 0.1

    if 'samples_number' not in st.session_state:
        st.session_state.samples_number = 100
