import streamlit as st
import pandas as pd
from formatterInputs import *
from control.matlab import tf, c2d, tfdata
from numpy import exp, ones, zeros


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

    sampling_time = st.session_state.sampling_time
    samples_number = st.session_state.samples_number

    st.header('Controle IMC')

    col1, col2 = st.columns([0.7, 0.3])

    with col1:

        sensor_data_with_elapsed_time = datetime_obj_to_elapsed_time()

        st.line_chart(data=sensor_data_with_elapsed_time, height=500)

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

        # IMC Controller Project

        # Initial Conditions
        angulo_sensor = zeros(samples_number)
        angulo_model1 = zeros(samples_number)
        angulo_model2 = zeros(samples_number)
        erro1 = zeros(samples_number)
        erro2 = zeros(samples_number)
        d0barra1 = zeros(samples_number)
        d0barra2 = zeros(samples_number)

        # Ajuste do taumf1 e taumf2
        ajuste1 = 0.6
        ajuste2 = 0.6

        angulo_ref = 50*ones(samples_number)
        # Power Saturation
        max_pot = 15
        min_pot = 7

        # Variável controlada
        pot_motor_1 = zeros(samples_number)
        pot_motor_2 = zeros(samples_number)
        delta_pot_motor_1 = zeros(samples_number)
        delta_pot_motor_2 = zeros(samples_number)
        u = ["0,0"]*samples_number
        u

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

        # Calculo do tau de malha fechada
        tau_mf1 = ajuste1*tausmith1
        alpha1 = exp(-sampling_time/tau_mf1)

        tau_mf2 = ajuste2*tausmith2
        alpha2 = exp(-sampling_time/tau_mf2)

        for k in range(2, samples_number):

            # ----- Sa�da da planta
            angulo_sensor[k] = -a1m1*angulo_model1[k-1] + b0m1*pot_motor_1[k-1]

            # ---- Saida do modelo
            angulo_model1[k] = -a1m1*angulo_model1[k-1] + b0m1*pot_motor_1[k-1]
            angulo_model2[k] = -a1m2*angulo_model2[k-1] - b0m2*pot_motor_2[k-1]

            # Determinar a incerteza
            d0barra1[k] = angulo_sensor[k] - angulo_model1[k]
            d0barra2[k] = -(angulo_sensor[k] - angulo_model2[k])

            # Determinar o Erro
            erro1[k] = angulo_ref[k] - d0barra1[k]
            erro2[k] = -(angulo_ref[k] + d0barra2[k])

            # Sinal de controle
            pot_motor_1[k] = alpha1*pot_motor_1[k-1] + ((1-alpha1)/b0m1)*erro1[k-1] + \
                a1m1*((1-alpha1)/b0m1)*erro1[k-2]

            pot_motor_2[k] = alpha2*pot_motor_2[k-1] + ((1-alpha2)/b0m2)*erro2[k-1] + \
                a1m2*((1-alpha2)/b0m2)*erro2[k-2]

            # Satura��es do sinal de Controle
            pot_motor_1[k] = max(min_pot, min(pot_motor_1[k], max_pot))
            pot_motor_2[k] = max(min_pot, min(pot_motor_2[k], max_pot))

            # Enviar sinal de controle para os motores
            u[k] = f"{pot_motor_1[k]},{pot_motor_2[k]}\r"
            u

            # Retirar dados do sensor errado
            if angulo_sensor[k] <= 0 or angulo_sensor[k] > 90:
                # Tratar os dados errados
                angulo_sensor[k] = angulo_sensor[k-1]

    st.line_chart(angulo_sensor)
    st.line_chart(pot_motor_1)
