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


def imc_Controller():

    st.header('Controle IMC')

    col1, col2 = st.columns([0.7, 0.3])

    with col2:

        tab1, tab2 = st.tabs(["Única Referência", "Múltiplas Referências"])
        with tab1:
            single_2reference = st.number_input(
                'Referência:', value=50, step=1, min_value=0, max_value=90, key='single_reference_imc')
        with tab2:
            col21, col22, col23 = st.columns(3)
            with col21:
                reference = st.number_input(
                    'Referência:', value=50, step=1, min_value=0, max_value=90, key='reference1_imc')

            with col22:
                reference2 = st.number_input(
                    'Referência 2:', value=50, step=1, min_value=0, max_value=90,
                    key='reference2_imc')

            with col23:
                reference3 = st.number_input(
                    'Referência 3:', value=50, step=1, min_value=0, max_value=90, key='reference3_imc')

        if st.button('Receber Dados'):
            imcControlProcess()

    with col1:

        sensor_data_with_elapsed_time = datetime_obj_to_elapsed_time()

        st.line_chart(data=sensor_data_with_elapsed_time, height=500)


def imcControlProcess():

    sampling_time = st.session_state.sampling_time
    samples_number = st.session_state.samples_number
    # IMC Controller Project

    # Initial Conditions
    angulo_sensor = zeros(samples_number)
    angulo_model1 = zeros(samples_number)
    angulo_model2 = zeros(samples_number)
    erro1 = zeros(samples_number)
    erro2 = zeros(samples_number)
    d0barra1 = zeros(samples_number)
    d0barra2 = zeros(samples_number)

    # taumf1 e taumf2 Ajusts
    ajuste1 = 0.6
    ajuste2 = 0.6

    # Setpoint
    angulo_ref = 50*ones(samples_number)

    # Power Saturation
    max_pot = 15
    min_pot = 7

    # Variável controlada
    pot_motor_1 = zeros(samples_number)
    pot_motor_2 = zeros(samples_number)
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
    tau_mf1 = ajuste1*tausmith1
    alpha1 = exp(-sampling_time/tau_mf1)

    tau_mf2 = ajuste2*tausmith2
    alpha2 = exp(-sampling_time/tau_mf2)

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
    sendToArduino(arduinoData, '0,0')

    while interation < samples_number:
        current_time = time.time()
        if current_time - start_time > sampling_time:
            start_time = current_time
            # -----  Angle Sensor Output
            angulo_sensor[interation] = readFromArduino(arduinoData)

            # ---- Motor Model Output
            angulo_model1[interation] = -a1m1 * \
                angulo_model1[interation-1] + \
                b0m1*pot_motor_1[interation-1]
            angulo_model2[interation] = -a1m2 * \
                angulo_model2[interation-1] - \
                b0m2*pot_motor_2[interation-1]

            # Determine uncertainty
            d0barra1[interation] = angulo_sensor[interation] - \
                angulo_model1[interation]
            d0barra2[interation] = - \
                (angulo_sensor[interation] - angulo_model2[interation])

            # Determine Error
            erro1[interation] = angulo_ref[interation] - \
                d0barra1[interation]
            erro2[interation] = - \
                (angulo_ref[interation] + d0barra2[interation])

            # Control Signal
            pot_motor_1[interation] = alpha1*pot_motor_1[interation-1] + ((1-alpha1)/b0m1)*erro1[interation-1] + \
                a1m1*((1-alpha1)/b0m1)*erro1[interation-2]

            pot_motor_2[interation] = alpha2*pot_motor_2[interation-1] + ((1-alpha2)/b0m2)*erro2[interation-1] + \
                a1m2*((1-alpha2)/b0m2)*erro2[interation-2]

            # Control Signal Saturation
            pot_motor_1[interation] = max(
                min_pot, min(pot_motor_1[interation], max_pot))
            pot_motor_2[interation] = max(
                min_pot, min(pot_motor_2[interation], max_pot))

            # Motor Power String Formatation
            motors_power_packet[interation] = f"{pot_motor_1[interation]},{pot_motor_2[interation]}\r"

            # Clean Sensor Data
            if angulo_sensor[interation] <= 0 or angulo_sensor[interation] > 90:
                angulo_sensor[interation] = angulo_sensor[interation-1]

            sendToArduino(arduinoData, motors_power_packet[interation])
            current_timestamp = datetime.datetime.now()
            sensor[str(current_timestamp)] = float(angulo_sensor[interation])
            interation += 1

            percent_complete = interation * 1 / samples_number
            my_bar.progress(percent_complete, text=progress_text)

    sendToArduino(arduinoData, '0,0')


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
