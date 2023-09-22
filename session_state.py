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

    if 'control_signal_1' not in st.session_state.controller_parameters:
        st.session_state.controller_parameters['control_signal_1'] = {}

    if 'control_signal_2' not in st.session_state.controller_parameters:
        st.session_state.controller_parameters['control_signal_2'] = {}
        
    if 'reference_input' not in st.session_state.controller_parameters:
        st.session_state.controller_parameters['reference_input'] = {}
        
    if 'saturation_max_value' not in st.session_state.controller_parameters:
        st.session_state.controller_parameters['saturation_max_value'] = {}
        
    if 'saturation_min_value' not in st.session_state.controller_parameters:
        st.session_state.controller_parameters['saturation_min_value'] = {}
        
    if 'process_output_sensor' not in st.session_state.controller_parameters:
        st.session_state.controller_parameters['process_output_sensor'] = {}
    

def get_session_variable(variable:str):
    
    session_variable = {

        "samples_number":           st.session_state.controller_parameters['samples_number'],
        "sampling_time":            st.session_state.controller_parameters['sampling_time'],
        "control_signal_1":         st.session_state.controller_parameters['control_signal_1'],
        "control_signal_2":         st.session_state.controller_parameters['control_signal_2'],
        "reference_input":          st.session_state.controller_parameters['reference_input'],
        "saturation_max_value":     st.session_state.controller_parameters['saturation_max_value'],
        "process_output_sensor":    st.session_state.controller_parameters['process_output_sensor'],
    }
    
    return session_variable[variable]