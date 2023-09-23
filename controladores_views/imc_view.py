import streamlit as st
import pandas as pd
from formatterInputs import *
from control.matlab import tf, c2d, tfdata
from numpy import exp, ones, zeros
from connections import *
import datetime
from session_state import get_session_variable


def datetime_obj_to_elapsed_time(variable:str)->dict:

    sensor_data_dict = get_session_variable(variable)
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

def dictionary_to_pandasDataframe(variable:dict,variable_name_column:str)->pd.DataFrame:

    # Convert the inner dictionary to a list of dictionaries
    data_list = [{"Time (s)": timestamp, f"{variable_name_column}": value} for timestamp, value in variable.items()]

    # Create a DataFrame from the list of dictionaries
    variable_dataframe = pd.DataFrame(data_list)
    return variable_dataframe

def insertReferenceInDataframe(variable_dataframe:pd.DataFrame,reference_col:list)->pd.DataFrame:

    # Convert the inner dictionary to a list of dictionaries
    variable_dataframe['Reference'] = reference_col

    return variable_dataframe

def dataframeToPlot(variable_dict:str,variable_name_to_plot:str, second_variable:str) -> pd.DataFrame:
    variable_with_time = datetime_obj_to_elapsed_time(variable_dict)
    process_dictionary = dictionary_to_pandasDataframe(variable_with_time,variable_name_to_plot)
    return insertReferenceInDataframe(process_dictionary,get_session_variable(second_variable))


def calculate_time_limit()->float:
    # Receber os valores de tempo de amostragem e número de amostras da sessão
    sampling_time = get_session_variable('sampling_time')
    samples_number = get_session_variable('samples_number')
    time_max_value = samples_number*sampling_time
    return time_max_value


def get_sample_position(sampling_time:float, samples_number:int, time_instant:float) -> int:
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

    st.header('Internal Model Control (IMC)')

    graphics_col, imc_config_col = st.columns([0.7, 0.3])

    with imc_config_col:
        st.write('### Configurações do Controlador')

        sisoSystemTab, mimoSystemTab = st.tabs(
            ["SISO", "MIMO"])
            #["Única Referência", "Múltiplas Referências"])
        
        with sisoSystemTab:
            
            transfer_function_type = st.radio('**Tipo de Função de Transferência**',['Continuo','Discreto'],horizontal=True,key='transfer_function_type')
            
            num_coeff = st.text_input('Coeficientes do **Numerador** da Função de Transferência do Modelo:',key='siso_imc_num_coeff')
            den_coeff = st.text_input('Coeficientes do **Denominador** da Função de Transferência do Modelo:',key='tiso_imc_den_coeff')
            
            reference_number = st.radio('Quantidade de referências',['Única','Múltiplas'],horizontal=True,key='reference_number')
            

            if reference_number == 'Única':
                imc_single_reference = st.number_input(
                'Referência:', value=50, step=1, min_value=0, max_value=90, key='imc_single_reference')
                
            else:
                col21, col22, col23 = st.columns(3)
                with col23:

                    imc_siso_multiple_reference3 = st.number_input(
                        'Referência 3:', value=30.0, step=1.0, min_value=0.0, max_value=90.0, key='siso_imc_multiple_reference3')

                with col22:
                    imc_siso_multiple_reference2 = st.number_input(
                        'Referência 2:', value=30.0, step=1.0, min_value=0.0, max_value=90.0,
                        key='siso_imc_multiple_reference2')

                with col21:
                    imc_siso_multiple_reference1 = st.number_input(
                        'Referência 1:', value=30.0, step=1.0, min_value=0.0, max_value=90.0, key='siso_imc_multiple_reference1')

                changeReferenceCol1, changeReferenceCol2 = st.columns(2)

                with changeReferenceCol2:
                    siso_change_ref_instant3 = st.number_input(
                        'Instante da referência 3 (s):', value=calculate_time_limit()/2, step=0.1, min_value=0.0, max_value=calculate_time_limit(), key='siso_change_ref_instant3')

                with changeReferenceCol1:
                    siso_change_ref_instant2 = st.number_input(
                        'Instante da referência 2 (s):', value=2.0, step=1.0, min_value=0.0, max_value=siso_change_ref_instant3, key='siso_change_ref_instant2')
                
            imc_sr_tau_mf1 = st.number_input(
                        'Constante de Tempo de Malha Fechada ($\\tau$)', value=0.9, step=0.1, min_value=0.0, max_value=1.0, key='imc_sr_tau_mf1')
            
            if st.button('Iniciar', type='primary', key='imc_siso_button'):
                if reference_number == 'Única':
                    imcControlProcessSISO(imc_sr_tau_mf1, imc_single_reference, imc_single_reference, imc_single_reference
                                            )
                    
                else:
                    imcControlProcessSISO(imc_sr_tau_mf1, imc_siso_multiple_reference1, imc_siso_multiple_reference2, imc_siso_multiple_reference3,
                                          siso_change_ref_instant2,siso_change_ref_instant3)

        with mimoSystemTab:
            col21, col22, col23 = st.columns(3)
            with col23:

                imc_multiple_reference3 = st.number_input(
                    'Referência 3:', value=30.0, step=1.0, min_value=0.0, max_value=90.0, key='imc_multiple_reference3')

            with col22:
                imc_multiple_reference2 = st.number_input(
                    'Referência 2:', value=30.0, step=1.0, min_value=0.0, max_value=90.0,
                    key='imc_multiple_reference2')

            with col21:
                imc_multiple_reference1 = st.number_input(
                    'Referência:', value=30.0, step=1.0, min_value=0.0, max_value=90.0, key='imc_multiple_reference1')

            changeReferenceCol1, changeReferenceCol2 = st.columns(2)

            with changeReferenceCol2:
                change_ref_instant3 = st.number_input(
                    'Instante da referência 3 (s):', value=calculate_time_limit()/2, step=0.1, min_value=0.0, max_value=calculate_time_limit(), key='change_ref_instant3')

            with changeReferenceCol1:
                change_ref_instant2 = st.number_input(
                    'Instante da referência 2 (s):', value=2.0, step=1.0, min_value=0.0, max_value=change_ref_instant3, key='change_ref_instant2')
            st.write('Constante de Tempo de Malha Fechada ($\\tau$)')
            tau_mf_col1, tau_mf_col2 = st.columns(2)
            with tau_mf_col1:
                imc_mr_tau_mf1 = st.number_input(
                    '$\\tau_1$', value=0.9, step=0.1, min_value=0.0, max_value=100.0, key='imc_mr_tau_mf1')
            with tau_mf_col2:
                imc_mr_tau_mf2 = st.number_input(
                    '$\\tau_2$', value=0.9, step=0.1, min_value=0.0, max_value=100.0, key='imc_mr_tau_mf2')

            if st.button('Receber Dados', type='primary', key='imc_multiples_setpoint_button'):
                # imcControlProcess()
                 imcControlProcessTISO(imc_multiple_reference1, imc_multiple_reference2, imc_multiple_reference3,
                                  change_ref_instant2, change_ref_instant3,
                                  imc_mr_tau_mf1, imc_mr_tau_mf2)

    with graphics_col:

        process_output_dataframe = dataframeToPlot('process_output_sensor','Process Output','reference_input')
        control_signal_with_elapsed_time = datetime_obj_to_elapsed_time('control_signal_1')
        st.subheader('Resposta do Sistema')
        st.line_chart(data=process_output_dataframe, x= 'Time (s)', y = ['Reference','Process Output'], height=400)
        
        st.subheader('Sinal de Controle')
        st.line_chart(control_signal_with_elapsed_time,height=200)
        st.line_chart(data= get_session_variable('control_signal_2'),height=200)
        




def imcControlProcessTISO(imc_multiple_reference1, imc_multiple_reference2, imc_multiple_reference3,
                      change_ref_instant2, change_ref_instant3,
                      imc_mr_tau_mf1, imc_mr_tau_mf2):

    # Receber os valores de tempo de amostragem e número de amostras da sessão
    sampling_time = st.session_state.controller_parameters['sampling_time']
    samples_number = st.session_state.controller_parameters['samples_number']

    # IMC Controller Project

    # Initial Conditions
    process_output = zeros(samples_number)
    model_output_1 = zeros(samples_number)
    model_output_2 = zeros(samples_number)
    erro1 = zeros(samples_number)
    erro2 = zeros(samples_number)
    output_model_comparation_1 = zeros(samples_number)
    output_model_comparation_2 = zeros(samples_number)

    # Take the index of time to change the referencee
    instant_sample_2 = get_sample_position(
        sampling_time, samples_number, change_ref_instant2)
    instant_sample_3 = get_sample_position(
        sampling_time, samples_number, change_ref_instant3)

    reference_input = imc_multiple_reference1*ones(samples_number)
    reference_input[instant_sample_2:instant_sample_3] = imc_multiple_reference2
    reference_input[instant_sample_3:] = imc_multiple_reference3
    st.session_state.controller_parameters['reference_input'] = reference_input

    # taumf1 e taumf2 Ajusts
    ajuste1 = 0.6
    ajuste2 = 0.6

    # Power Saturation
    max_pot = 15
    min_pot = 7

    # Manipulated variable
    manipulated_variable_1 = zeros(samples_number)
    manipulated_variable_2 = zeros(samples_number)
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
    #tau_mf1 = imc_mr_tau_mf1
    alpha1 = exp(-sampling_time/tau_mf1)

    tau_mf2 = ajuste2*tausmith2
    #tau_mf2 = imc_mr_tau_mf1
    alpha2 = exp(-sampling_time/tau_mf2)

    # Receber o objeto arduino da sessão
    arduinoData = st.session_state.connected['arduinoData']

    # limpar os valores anteriores do sensor
    st.session_state.sensor = dict()
    sensor = st.session_state.sensor

    
    # clear previous control signal values
    st.session_state.controller_parameters['control_signal_1']= dict()
    control_signal_1 = st.session_state.controller_parameters['control_signal_1']
    
    
    # clear previous control signal values
    st.session_state.controller_parameters['control_signal_2']= dict()
    control_signal_2 = st.session_state.controller_parameters['control_signal_2']
    
    
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
            model_output_1[interation] = -a1m1 * model_output_1[interation-1] + b0m1*manipulated_variable_1[interation-1]
            model_output_2[interation] = -a1m2 * model_output_2[interation-1] - b0m2*manipulated_variable_2[interation-1]

            # Determine uncertainty
            output_model_comparation_1[interation] = process_output[interation] - model_output_1[interation]
            output_model_comparation_2[interation] = -(process_output[interation] - model_output_2[interation])

            # Determine Error
            erro1[interation] = reference_input[interation] - output_model_comparation_1[interation]
            erro2[interation] = - (reference_input[interation] + output_model_comparation_2[interation])

            # Control Signal
            manipulated_variable_1[interation] = alpha1*manipulated_variable_1[interation-1] + ((1-alpha1)/b0m1)*erro1[interation] + \
                                            a1m1*((1-alpha1)/b0m1)*erro1[interation-1]

            manipulated_variable_2[interation] = alpha2*manipulated_variable_2[interation-1] + ((1-alpha2)/b0m2)*erro2[interation] + \
                                            a1m2*((1-alpha2)/b0m2)*erro2[interation-1]

            # Control Signal Saturation
            manipulated_variable_1[interation] = max(
                min_pot, min(manipulated_variable_1[interation], max_pot))
            manipulated_variable_2[interation] = max(
                min_pot, min(manipulated_variable_2[interation], max_pot))

            # Motor Power String Formatation
            motors_power_packet[interation] = f"{manipulated_variable_1[interation]},{manipulated_variable_2[interation]}\r"

            # Clean Sensor Data
            if process_output[interation] <= 0 or process_output[interation] > 90:
                process_output[interation] = process_output[interation-1]

            sendToArduino(arduinoData, motors_power_packet[interation])
            current_timestamp = datetime.datetime.now()
            sensor[str(current_timestamp)] = float(process_output[interation])
            control_signal_1[str(current_timestamp)] = float(manipulated_variable_1[interation])
            control_signal_2[str(current_timestamp)] = float(manipulated_variable_2[interation])
            interation += 1

            percent_complete = interation * 1 / samples_number
            my_bar.progress(percent_complete, text=progress_text)

    # Turn off the motor
    sendToArduino(arduinoData, '0,0')



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
            angulo_model1[interation] = -a1m1 * angulo_model1[interation-1] +  b0m1*pot_motor_1[interation-1]
            angulo_model2[interation] = -a1m2 * angulo_model2[interation-1] -  b0m2*pot_motor_2[interation-1]

            # Determine uncertainty
            d0barra1[interation] = angulo_sensor[interation] -  angulo_model1[interation]
            d0barra2[interation] = -  (angulo_sensor[interation] - angulo_model2[interation])

            # Determine Error
            erro1[interation] = angulo_ref[interation] -  d0barra1[interation]
            erro2[interation] = -  (angulo_ref[interation] + d0barra2[interation])

            # Control Signal
            pot_motor_1[interation] = alpha1*pot_motor_1[interation-1] + ((1-alpha1)/b0m1)*erro1[interation] +  a1m1*((1-alpha1)/b0m1)*erro1[interation-1]

            pot_motor_2[interation] = alpha2*pot_motor_2[interation-1] + ((1-alpha2)/b0m2)*erro2[interation] +  a1m2*((1-alpha2)/b0m2)*erro2[interation-1]

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



def imcControlProcessSISO(  imc_mr_tau_mf1, imc_multiple_reference1, imc_multiple_reference2, imc_multiple_reference3,
                            change_ref_instant2 = 1, change_ref_instant3 = 1):

    # Receber os valores de tempo de amostragem e número de amostras da sessão
    sampling_time = get_session_variable('sampling_time')
    samples_number = get_session_variable('samples_number')

    # IMC Controller Project

    # Initial Conditions
    process_output = zeros(samples_number)
    model_output_1 = zeros(samples_number)
    erro1 = zeros(samples_number)
    output_model_comparation = zeros(samples_number)

    # Take the index of time to change the referencee
    instant_sample_2 = get_sample_position(sampling_time, samples_number, change_ref_instant2)
    instant_sample_3 = get_sample_position(sampling_time, samples_number, change_ref_instant3)

    reference_input = imc_multiple_reference1*ones(samples_number)
    reference_input[instant_sample_2:instant_sample_3] = imc_multiple_reference2
    reference_input[instant_sample_3:] = imc_multiple_reference3
    
    st.session_state.controller_parameters['reference_input'] = reference_input

    # taumf1 e taumf2 Ajusts
    ajuste1 = 1

    # Power Saturation
    max_pot = get_session_variable('saturation_max_value')
    min_pot = get_session_variable('saturation_min_value')

    # Manipulated variable
    manipulated_variable_1 = zeros(samples_number)
    motors_power_packet = ["0,0"]*samples_number

    # Coefiientes do Modelo Smith motor 1
    Kpsmith1 = 0.9995
    thetasmith1 = 0.65
    tausmith1 =  1.809


    # Motor 1 Model Transfer Function
    Gm1 = tf(Kpsmith1, [tausmith1, 1])
    Gmz1 = c2d(Gm1, sampling_time)
    num1, den1 = tfdata(Gmz1)
    Bm1 = num1[0][0]
    Am1 = den1[0][0]
    b0m1 = Bm1[0]
    a1m1 = Am1[1]


    # Close Loop Tau Calculation
    # tau_mf1 = ajuste1*tausmith1
    tau_mf1 = imc_mr_tau_mf1
    alpha1 = exp(-sampling_time/tau_mf1)
    

    # Receive the Arduino object from the session
    arduinoData = st.session_state.connected['arduinoData']

    # clear previous control signal values
    st.session_state.controller_parameters['control_signal_1']= dict()
    control_signal_1 = st.session_state.controller_parameters['control_signal_1']
    
    # clear previous control signal values
    st.session_state.controller_parameters['process_output_sensor'] = dict()
    process_output_sensor = st.session_state.controller_parameters['process_output_sensor']

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
            model_output_1[interation] = -a1m1 * model_output_1[interation-1] + b0m1*manipulated_variable_1[interation-1]

            # Determine uncertainty
            output_model_comparation[interation] = process_output[interation] - model_output_1[interation]

            # Determine Error
            erro1[interation] = reference_input[interation] - output_model_comparation[interation]

            # Control Signal
            manipulated_variable_1[interation] = alpha1*manipulated_variable_1[interation-1] + ((1-alpha1)/b0m1)*erro1[interation] + \
                                                a1m1*((1-alpha1)/b0m1)*erro1[interation-1]


            # Control Signal Saturation
            manipulated_variable_1[interation] = max(min_pot, min(manipulated_variable_1[interation], max_pot))
           

            # Motor Power String Formatation
            motors_power_packet[interation] = f"{manipulated_variable_1[interation]}\r"

            # Clean Sensor Data
            if process_output[interation] <= 0 or process_output[interation] > 90:
                process_output[interation] = process_output[interation-1]

            sendToArduino(arduinoData, motors_power_packet[interation])
            
            # Store the output process values and 
            current_timestamp = datetime.datetime.now()
            process_output_sensor[str(current_timestamp)] = float(process_output[interation])
            control_signal_1[str(current_timestamp)] = float(manipulated_variable_1[interation])
            interation += 1

            percent_complete = interation * 1 / samples_number
            my_bar.progress(percent_complete, text=progress_text)

    # Turn off the motor
    sendToArduino(arduinoData, '0,0')
