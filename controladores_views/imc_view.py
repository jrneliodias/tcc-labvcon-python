import streamlit as st
import pandas as pd
from formatterInputs import *
from control.matlab import tf, c2d, tfdata
from numpy import exp, ones, zeros
from connections import *
import datetime


def datetime_obj_to_elapsed_time():

    sensor_data_dict = st.session_state.sensor
    date_object = keys2DatetimeObj(sensor_data_dict)

    time_interval = [0] + [(date_object[i] - date_object[0]).total_seconds()
                           for i in range(1, len(date_object))]

    # sensor_formatted2Hours_dict = {
    #     key.split()[1]: value
    #     for key, value in sensor_dict.items()
    # }

    elapsed_time_in_sec = {time_interval[i]: sensor_data_dict[key]
                           for i, key in enumerate(sensor_data_dict)}

    return elapsed_time_in_sec


def calculate_time_limit():
    # Receber os valores de tempo de amostragem e número de amostras da sessão
    sampling_time = st.session_state.sampling_time
    samples_number = st.session_state.samples_number
    time_max_value = samples_number*sampling_time
    return time_max_value


def get_sample_position(sampling_time, samples_number, time_instant):
    """
    Calculate the position (index) of a given time instant in the sampled data.

    Parameters:
    - sampling_time: The time between each sample.
    - samples_number: The total number of samples.
    - time_instant: The time instant for which you want to find the sample position.

    Returns:
    - The position (index) of the sample corresponding to the given time instant.
    """
    if time_instant < 0:
        return 0  # Handle negative time instant

    # Calculate the position based on the time instant and sampling time
    position = int(time_instant / sampling_time)

    # Ensure the position is within the valid range [0, samples_number-1]
    position = max(0, min(position, samples_number - 1))

    return position


def imc_Controller_Interface():

    st.header('Internal Model Control (IMC) - Two Input Single Output (TISO)')

    graphics_col, imc_config_col = st.columns([0.7, 0.3])

    with imc_config_col:
        st.write('### Configurações do Controlador')

        singleRefTab, MultipleRefTab = st.tabs(
            ["Única Referência", "Múltiplas Referências"])
        with singleRefTab:

            imc_single_reference = st.number_input(
                'Referência:', value=50, step=1, min_value=0, max_value=90, key='imc_single_reference')

            st.write('Constante de Tempo de Malha Fechada ($\\tau$)')
            col11, col12 = st.columns(2)

            with col11:
                imc_sr_tau_mf1 = st.number_input(
                    '$\\tau_1$', value=0.9, step=0.1, min_value=0.0, max_value=1.0, key='imc_sr_tau_mf1')
            with col12:
                imc_sr_tau_mf2 = st.number_input(
                    '$\\tau_2$', value=0.9, step=0.1, min_value=0.0, max_value=1.0, key='imc_sr_tau_mf2')

            if st.button('Receber Dados', type='primary', key='imc_single_setpoint_button'):
                imcControlProcess()

        with MultipleRefTab:
            col21, col22, col23 = st.columns(3)
            with col23:

                imc_multiple_reference3 = st.number_input(
                    'Referência 3:', value=30, step=1, min_value=0, max_value=90, key='imc_multiple_reference3')

            with col22:
                imc_multiple_reference2 = st.number_input(
                    'Referência 2:', value=30, step=1, min_value=0, max_value=90,
                    key='imc_multiple_reference2')

            with col21:
                imc_multiple_reference1 = st.number_input(
                    'Referência:', value=30, step=1, min_value=0, max_value=90, key='imc_multiple_reference1')

            changeReferenceCol1, changeReferenceCol2 = st.columns(2)

            with changeReferenceCol2:
                change_ref_instant3 = st.number_input(
                    'Instante da referência 3 (s):', value=calculate_time_limit()/2, step=0.1, min_value=0.0, max_value=calculate_time_limit(), key='change_ref_instant3')

            with changeReferenceCol1:
                change_ref_instant2 = st.number_input(
                    'Instante da referência 2 (s):', value=2.0, step=1.0, min_value=0.0, max_value=change_ref_instant3, key='change_ref_instant2')
            st.write('Constante de Tempo de Malha Fechada ($\\tau$)')
            col24, col25 = st.columns(2)
            with col24:
                imc_mr_tau_mf1 = st.number_input(
                    '$\\tau_1$', value=0.9, step=0.1, min_value=0.0, max_value=100.0, key='imc_mr_tau_mf1')
            with col25:
                imc_mr_tau_mf2 = st.number_input(
                    '$\\tau_2$', value=0.9, step=0.1, min_value=0.0, max_value=100.0, key='imc_mr_tau_mf2')

            if st.button('Receber Dados', type='primary', key='imc_multiples_setpoint_button'):
                imcControlProcess(imc_multiple_reference1, imc_multiple_reference2, imc_multiple_reference3,
                                  change_ref_instant2, change_ref_instant3,
                                  imc_mr_tau_mf1, imc_mr_tau_mf2)

    with graphics_col:

        sensor_data_with_elapsed_time = datetime_obj_to_elapsed_time()
        st.subheader('Resposta do Sistema')
        st.line_chart(data=sensor_data_with_elapsed_time, height=500)
        st.subheader('Sinal de Controle')
        st.line_chart(
            data=st.session_state.controller_parameters['control_signal_1'])
        st.line_chart(
            data=st.session_state.controller_parameters['control_signal_2'])


def imcControlProcess(imc_multiple_reference1, imc_multiple_reference2, imc_multiple_reference3,
                      change_ref_instant2, change_ref_instant3,
                      imc_mr_tau_mf1, imc_mr_tau_mf2):

    # Receber os valores de tempo de amostragem e número de amostras da sessão
    sampling_time = st.session_state.sampling_time
    samples_number = st.session_state.samples_number
    reference_input = st.session_state.reference_input

    # IMC Controller Project

    # Initial Conditions
    process_output = zeros(samples_number)
    model_output_1 = zeros(samples_number)
    model_output_2 = zeros(samples_number)
    erro1 = zeros(samples_number)
    erro2 = zeros(samples_number)
    d0barra1 = zeros(samples_number)
    d0barra2 = zeros(samples_number)

    # Take the index of time to change the referencee
    instant_sample_2 = get_sample_position(
        sampling_time, samples_number, change_ref_instant2)
    instant_sample_3 = get_sample_position(
        sampling_time, samples_number, change_ref_instant3)

    reference_input = imc_multiple_reference1*ones(samples_number)
    reference_input[instant_sample_2:instant_sample_3] = imc_multiple_reference2
    reference_input[instant_sample_3:] = imc_multiple_reference3

    # taumf1 e taumf2 Ajusts
    ajuste1 = 0.6
    ajuste2 = 0.6

    # Power Saturation
    max_pot = 15
    min_pot = 7

    # Variável controlada
    control_signal_1 = zeros(samples_number)
    control_signal_2 = zeros(samples_number)
    motors_power_packet = ["0,0"]*samples_number

    # Coefiientes do Modelo Smith motor 1
    Kpsmith1 = 7.737
    thetasmith1 = 0.65
    tausmith1 = 0.6

    # Coefiientes do Modelo Smith motor 2
    Kpsmith2 = 12.86
    thetasmith2 = 0.5
    tausmith2 = 0.66

    # Motor 1 Model Transfer Function
    Gm1 = tf(Kpsmith1, [tausmith1, 1])
    Gmz1 = c2d(Gm1, sampling_time)
    num1, den1 = tfdata(Gmz1)
    Bm1 = num1[0][0]
    Am1 = den1[0][0]
    b0m1 = Bm1[0]
    a1m1 = Am1[1]

    # Motor 2 Model Transfer Function
    Gm2 = tf(Kpsmith2, [tausmith2, 1])
    Gmz2 = c2d(Gm2, sampling_time)
    num2, den2 = tfdata(Gmz2)
    Bm2 = num2[0][0]
    Am2 = den2[0][0]
    b0m2 = Bm2[0]
    a1m2 = Am2[1]

    # Close Loop Tau Calculation
    # tau_mf1 = ajuste1*tausmith1
    tau_mf1 = imc_mr_tau_mf1
    alpha1 = exp(-sampling_time/tau_mf1)

    # tau_mf2 = ajuste2*tausmith2
    tau_mf2 = imc_mr_tau_mf1
    alpha2 = exp(-sampling_time/tau_mf2)

    # Receber o objeto arduino da sessão
    arduinoData = st.session_state.connected['arduinoData']

    # limpar os valores anteriores do sensor
    st.session_state.sensor = dict()
    sensor = st.session_state.sensor

    # inicializar  o timer
    start_time = time.time()
    interation = 0

    # Inicializar a barra de progresso
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)
    
    # receive the first mesure 
    sendToArduino(arduinoData, '0,0')

    while interation < samples_number:
        current_time = time.time()
        if current_time - start_time > sampling_time:
            start_time = current_time
            # -----  Angle Sensor Output
            process_output[interation] = readFromArduino(arduinoData)

            # ---- Motor Model Output
            model_output_1[interation] = -a1m1 * model_output_1[interation-1] + b0m1*control_signal_1[interation-1]
            model_output_2[interation] = -a1m2 * model_output_2[interation-1] - b0m2*control_signal_2[interation-1]

            # Determine uncertainty
            d0barra1[interation] = process_output[interation] - model_output_1[interation]
            d0barra2[interation] = -(process_output[interation] - model_output_2[interation])

            # Determine Error
            erro1[interation] = reference_input[interation] - d0barra1[interation]
            erro2[interation] = - (reference_input[interation] + d0barra2[interation])

            # Control Signal
            control_signal_1[interation] = alpha1*control_signal_1[interation-1] + ((1-alpha1)/b0m1)*erro1[interation-1] + \
                                            a1m1*((1-alpha1)/b0m1)*erro1[interation-2]

            control_signal_2[interation] = alpha2*control_signal_2[interation-1] + ((1-alpha2)/b0m2)*erro2[interation-1] + \
                                            a1m2*((1-alpha2)/b0m2)*erro2[interation-2]

            # Control Signal Saturation
            control_signal_1[interation] = max(
                min_pot, min(control_signal_1[interation], max_pot))
            control_signal_2[interation] = max(
                min_pot, min(control_signal_2[interation], max_pot))

            # Motor Power String Formatation
            motors_power_packet[interation] = f"{control_signal_1[interation]},{control_signal_2[interation]}\r"

            # Clean Sensor Data
            if process_output[interation] <= 0 or process_output[interation] > 90:
                process_output[interation] = process_output[interation-1]

            sendToArduino(arduinoData, motors_power_packet[interation])
            current_timestamp = datetime.datetime.now()
            sensor[str(current_timestamp)] = float(process_output[interation])
            interation += 1

            percent_complete = interation * 1 / samples_number
            my_bar.progress(percent_complete, text=progress_text)

    # Turn off the motor
    sendToArduino(arduinoData, '0,0')
