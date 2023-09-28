import streamlit as st
import pandas as pd
from formatterInputs import *
from control.matlab import tf, c2d, tfdata
from numpy import exp, ones, zeros,array, dot, convolve
from connections import *
import datetime
from session_state import get_session_variable




def imc_Controller_Interface():

    st.header('Internal Model Control (IMC)')

    graphics_col, imc_config_col = st.columns([0.7, 0.3])

    with imc_config_col:
        st.write('### Configurações do Controlador')

        sisoSystemTab, mimoSystemTab = st.tabs(["SISO", "MIMO"])
            #["Única Referência", "Múltiplas Referências"])
        
        with sisoSystemTab:
            
            transfer_function_type = st.radio('**Tipo de Função de Transferência**',['Continuo','Discreto'],horizontal=True,key='transfer_function_type')
            
            help_text = 'Valores decimais como **0.9** ou **0.1, 0.993**. Para múltiplos valores, vírgula é necessário.'
            num_coeff = st.text_input('Coeficientes do **Numerador** da Função de Transferência do Modelo:',key='siso_imc_num_coeff',help=help_text,placeholder='0.994')
            
            coefficients_validations(num_coeff)
                
            den_coeff = st.text_input('Coeficientes do **Denominador** da Função de Transferência do Modelo:',key='siso_imc_den_coeff',help=help_text,placeholder='1.334 , 1')
            coefficients_validations(den_coeff)
            
            delay_checkbox_col, delay_input_col = st.columns(2)
            with delay_checkbox_col:
                delay_checkbox=st.checkbox('Atraso de Transporte?')
                
            with delay_input_col:
                if delay_checkbox:
                    delay_input = st.number_input(label='delay',key='delay_input',label_visibility='collapsed')
                    
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
                        'Instante da referência 3 (s):', value=calculate_time_limit()*3/4, step=0.1, min_value=0.0, max_value=calculate_time_limit(), key='siso_change_ref_instant3')

                with changeReferenceCol1:
                    siso_change_ref_instant2 = st.number_input(
                        'Instante da referência 2 (s):', value=calculate_time_limit()/2,step=1.0, min_value=0.0, max_value=siso_change_ref_instant3, key='siso_change_ref_instant2')
                
            imc_sr_tau_mf1 = st.number_input(
                        'Constante de Tempo de Malha Fechada ($\\tau$)', value=0.9, step=0.1, min_value=0.0, key='imc_sr_tau_mf1')
            
            if st.button('Iniciar', type='primary', key='imc_siso_button'):
                
                if reference_number == 'Única':
                    
                    imcControlProcessSISO(transfer_function_type,num_coeff,den_coeff,imc_sr_tau_mf1, imc_single_reference, imc_single_reference, imc_single_reference)
                    
                elif reference_number == 'Múltiplas':
                    imcControlProcessSISO(transfer_function_type,num_coeff,den_coeff,imc_sr_tau_mf1, imc_siso_multiple_reference1, imc_siso_multiple_reference2, imc_siso_multiple_reference3, siso_change_ref_instant2,siso_change_ref_instant3)

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
                    'Instante da referência 3 (s):', value=calculate_time_limit()*3/4, step=0.1, min_value=0.0, max_value=calculate_time_limit(), key='change_ref_instant3')

            with changeReferenceCol1:
                change_ref_instant2 = st.number_input(
                    'Instante da referência 2 (s):', value=calculate_time_limit()/2, step=1.0, min_value=0.0, max_value=change_ref_instant3, key='change_ref_instant2')
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
        st.subheader('Resposta do Sistema')
        plot_chart_validation(process_output_dataframe, x = 'Time (s)', y = ['Reference','Process Output'],height=500)
                
        st.subheader('Sinal de Controle')
        control_signal_with_elapsed_time = datetime_obj_to_elapsed_time('control_signal_1')
        control_signal_1_dataframe = dictionary_to_pandasDataframe(control_signal_with_elapsed_time,'Control Signal 1')
        
        
        plot_chart_validation(control_signal_1_dataframe, x = 'Time (s)', y = 'Control Signal 1',height=200)

      
def coefficients_validations(coeff_string):
    if  coeff_string == '':
        return None
    if not validateFloatInput(coeff_string):
        return st.error('''Insira valores decimais separados por vírgula.     
                        ex:  0.9 , 0.134''')

def plot_chart_validation(plot_variable,y:str,height= 200, x = 'Time (s)'):
    if plot_variable is None:
        return None
    if plot_variable.empty:
        return None
    
    return st.line_chart(data= plot_variable,x = x, y = y,height=height)

def convert_tf_2_discrete(num_coeff:str,den_coeff:str,tf_type:str):
    num_coeff_float = string2floatArray(num_coeff)
    den_coeff_float = string2floatArray(den_coeff)

    if tf_type == 'Discreto':
        return num_coeff_float, den_coeff_float
    
    sampling_time = get_session_variable('sampling_time')
    
    # Motor 1 Model Transfer Function
    Gm1 = tf(num_coeff_float, den_coeff_float)
    Gmz1 = c2d(Gm1, sampling_time)
    num1, den1 = tfdata(Gmz1)
    Bm1 = num1[0][0]
    Am1 = den1[0][0]
    return Am1, Bm1

def validateFloatInput(input_numbers_str:str):
    if ',' in input_numbers_str:
        parts = input_numbers_str.split(',')
    
        for part in parts:
            part = part.strip()
            try:
                float(part)
            except ValueError:
                return False
        
        return True
    
    else:
        try:
            float(input_numbers_str)
        except ValueError:
            return False
        return True


def string2floatArray(input_numbers_str:str) -> list[float] | float:
    '''
    Split the input string into an array of numbers
    '''
    if ',' in input_numbers_str:
        return [float(num.strip()) for num in input_numbers_str.split(',')]
    else:
        return float(input_numbers_str)
    
    

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
    kk = 0

    # Inicializar a barra de progresso
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)
    
    # receive the first mesure 
    sendToArduino(arduinoData, '0,0')

    while kk < samples_number:
        current_time = time.time()
        if current_time - start_time > sampling_time:
            start_time = current_time
            # -----  Angle Sensor Output
            process_output[kk] = readFromArduino(arduinoData)

            # ---- Motor Model Output
            model_output_1[kk] = -a1m1 * model_output_1[kk-1] + b0m1*manipulated_variable_1[kk-1]
            model_output_2[kk] = -a1m2 * model_output_2[kk-1] - b0m2*manipulated_variable_2[kk-1]

            # Determine uncertainty
            output_model_comparation_1[kk] = process_output[kk] - model_output_1[kk]
            output_model_comparation_2[kk] = -(process_output[kk] - model_output_2[kk])

            # Determine Error
            erro1[kk] = reference_input[kk] - output_model_comparation_1[kk]
            erro2[kk] = - (reference_input[kk] + output_model_comparation_2[kk])

            # Control Signal
            manipulated_variable_1[kk] = alpha1*manipulated_variable_1[kk-1] + ((1-alpha1)/b0m1)*erro1[kk] + \
                                            a1m1*((1-alpha1)/b0m1)*erro1[kk-1]

            manipulated_variable_2[kk] = alpha2*manipulated_variable_2[kk-1] + ((1-alpha2)/b0m2)*erro2[kk] + \
                                            a1m2*((1-alpha2)/b0m2)*erro2[kk-1]

            # Control Signal Saturation
            manipulated_variable_1[kk] = max(
                min_pot, min(manipulated_variable_1[kk], max_pot))
            manipulated_variable_2[kk] = max(
                min_pot, min(manipulated_variable_2[kk], max_pot))

            # Motor Power String Formatation
            motors_power_packet[kk] = f"{manipulated_variable_1[kk]},{manipulated_variable_2[kk]}\r"

            # Clean Sensor Data
            if process_output[kk] <= 0 or process_output[kk] > 90:
                process_output[kk] = process_output[kk-1]

            sendToArduino(arduinoData, motors_power_packet[kk])
            current_timestamp = datetime.datetime.now()
            sensor[str(current_timestamp)] = float(process_output[kk])
            control_signal_1[str(current_timestamp)] = float(manipulated_variable_1[kk])
            control_signal_2[str(current_timestamp)] = float(manipulated_variable_2[kk])
            kk += 1

            percent_complete = kk * 1 / samples_number
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
    kk = 0

    # Inicializar a barra de progresso
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)
    sendToArduino(arduinoData, '0,0')

    while kk < samples_number:
        current_time = time.time()
        if current_time - start_time > sampling_time:
            start_time = current_time
            # -----  Angle Sensor Output
            angulo_sensor[kk] = readFromArduino(arduinoData)

            # ---- Motor Model Output
            angulo_model1[kk] = -a1m1 * angulo_model1[kk-1] +  b0m1*pot_motor_1[kk-1]
            angulo_model2[kk] = -a1m2 * angulo_model2[kk-1] -  b0m2*pot_motor_2[kk-1]

            # Determine uncertainty
            d0barra1[kk] = angulo_sensor[kk] -  angulo_model1[kk]
            d0barra2[kk] = -  (angulo_sensor[kk] - angulo_model2[kk])

            # Determine Error
            erro1[kk] = angulo_ref[kk] -  d0barra1[kk]
            erro2[kk] = -  (angulo_ref[kk] + d0barra2[kk])

            # Control Signal
            pot_motor_1[kk] = alpha1*pot_motor_1[kk-1] + ((1-alpha1)/b0m1)*erro1[kk] +  a1m1*((1-alpha1)/b0m1)*erro1[kk-1]

            pot_motor_2[kk] = alpha2*pot_motor_2[kk-1] + ((1-alpha2)/b0m2)*erro2[kk] +  a1m2*((1-alpha2)/b0m2)*erro2[kk-1]

            # Control Signal Saturation
            pot_motor_1[kk] = max(
                min_pot, min(pot_motor_1[kk], max_pot))
            pot_motor_2[kk] = max(
                min_pot, min(pot_motor_2[kk], max_pot))

            # Motor Power String Formatation
            motors_power_packet[kk] = f"{pot_motor_1[kk]},{pot_motor_2[kk]}\r"

            # Clean Sensor Data
            if angulo_sensor[kk] <= 0 or angulo_sensor[kk] > 90:
                angulo_sensor[kk] = angulo_sensor[kk-1]

            sendToArduino(arduinoData, motors_power_packet[kk])
            current_timestamp = datetime.datetime.now()
            sensor[str(current_timestamp)] = float(angulo_sensor[kk])
            kk += 1

            percent_complete = kk * 1 / samples_number
            my_bar.progress(percent_complete, text=progress_text)

    sendToArduino(arduinoData, '0,0')



def imcControlProcessSISO(transfer_function_type:str,num_coeff:str,den_coeff:str,  imc_mr_tau_mf1:float, imc_multiple_reference1:float, imc_multiple_reference2:float, imc_multiple_reference3:float,change_ref_instant2 = 1, change_ref_instant3 = 1):
    
    if num_coeff == '':
        return st.error('Coeficientes incorretos no Numerador.')
    
    if den_coeff =='':
        return st.error('Coeficientes incorretos no Denominador.')

    # Receber os valores de tempo de amostragem e número de amostras da sessão
    sampling_time = get_session_variable('sampling_time')
    samples_number = get_session_variable('samples_number')

    # IMC Controller Project

    # Initial Conditions
    process_output = zeros(samples_number)
    model_output_1 = zeros(samples_number)
    erro1 = zeros(samples_number+1)
    output_model_comparation = zeros(samples_number)

    # Take the index of time to change the referencee
    instant_sample_2 = get_sample_position(sampling_time, samples_number, change_ref_instant2)
    instant_sample_3 = get_sample_position(sampling_time, samples_number, change_ref_instant3)

    reference_input = imc_multiple_reference1*ones(samples_number)
    reference_input[instant_sample_2:instant_sample_3] = imc_multiple_reference2
    reference_input[instant_sample_3:] = imc_multiple_reference3
    
    st.session_state.controller_parameters['reference_input'] = reference_input.tolist()

    # Power Saturation
    max_pot = get_session_variable('saturation_max_value')
    min_pot = get_session_variable('saturation_min_value')

    # Manipulated variable
    manipulated_variable_1 = zeros(samples_number)
    motors_power_packet = "0"

    A_coeff, B_coeff = convert_tf_2_discrete(num_coeff,den_coeff,transfer_function_type)
    
    # print(A_coeff)
    # print(B_coeff)
    A_order = len(A_coeff)-1
    B_order = len(B_coeff) # Zero holder aumenta um grau
    
    # Close Loop Tau Calculation
    # tau_mf1 = ajuste1*tausmith1
    tau_mf1 = imc_mr_tau_mf1
    alpha1 = exp(-sampling_time/tau_mf1)
    
    # Perform polynomial multiplication using np.convolve
    alpha_delta = [1,-alpha1]
    B_delta = convolve(B_coeff,alpha_delta)
    
    
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
    kk = 0

    # Inicializar a barra de progresso
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)
    
    # receive the first mesure 
    sendToArduino(arduinoData, "0")
    

    while kk < samples_number:
        current_time = time.time()
        if current_time - start_time > sampling_time:
            start_time = current_time
            
            # -----  Angle Sensor Output
            # print(f'kk = {kk}')
            process_output[kk] = readFromArduino(arduinoData)

            
            if kk <= A_order:
                # Store the output process values and control signal
                current_timestamp = datetime.datetime.now()
                process_output_sensor[str(current_timestamp)] = float(process_output[kk])
                control_signal_1[str(current_timestamp)] = float(manipulated_variable_1[kk])
                kk += 1

                percent_complete = kk / (samples_number)
                my_bar.progress(percent_complete, text=progress_text)
                
                sendToArduino(arduinoData, '0')
                

            # ---- Motor Model Output
            elif kk == 1 and A_order == 1:
                model_output_1[kk] = dot(-A_coeff[1:], model_output_1[kk-1::-1])\
                                        + dot(B_coeff, manipulated_variable_1[kk-1::-1])
                # Determine uncertainty
                output_model_comparation[kk] = process_output[kk] - model_output_1[kk]

                # Determine Error
                erro1[kk] = reference_input[kk] - output_model_comparation[kk]

                # Control Signal
                manipulated_variable_1[kk] = dot(-B_delta[1:],manipulated_variable_1[kk-1::-1])+ (1-alpha1)*dot(A_coeff,erro1[kk::-1])
                manipulated_variable_1[kk] = manipulated_variable_1[kk]/B_delta[0]
                # Control Signal Saturation
                manipulated_variable_1[kk] = max(min_pot, min(manipulated_variable_1[kk], max_pot))
            

                # Motor Power String Formatation
                motors_power_packet = f"{manipulated_variable_1[kk]}\r"

                sendToArduino(arduinoData, motors_power_packet)
                
                # Store the output process values and control signal
                current_timestamp = datetime.datetime.now()
                process_output_sensor[str(current_timestamp)] = float(process_output[kk])
                control_signal_1[str(current_timestamp)] = float(manipulated_variable_1[kk])
                kk += 1

                percent_complete = kk / (samples_number)
                my_bar.progress(percent_complete, text=progress_text)
                                        
            elif kk >A_order:
                
                # print(f'kk == {kk}')
                # print(f'model_output_1: {model_output_1[kk-1:kk-A_order-1:-1]}')
                # print(f'manipulated_variable_1: {manipulated_variable_1[kk-1:kk-B_order-1:-1]}')
                model_output_1[kk] = dot(-A_coeff[1:], model_output_1[kk-1:kk-A_order-1:-1])\
                                        + dot(B_coeff, manipulated_variable_1[kk-1:kk-B_order-1:-1])
                

                # Determine uncertainty
                output_model_comparation[kk] = process_output[kk] - model_output_1[kk]

                # Determine Error
                erro1[kk] = reference_input[kk] - output_model_comparation[kk]

                # Control Signal
                manipulated_variable_1[kk] = dot(-B_delta[1:],manipulated_variable_1[kk-1:kk-B_order-1:-1])+ (1-alpha1)*dot(A_coeff,erro1[kk:kk-A_order-1:-1])
                manipulated_variable_1[kk] = manipulated_variable_1[kk]/B_delta[0]
                # Control Signal Saturation
                manipulated_variable_1[kk] = max(min_pot, min(manipulated_variable_1[kk], max_pot))
            

                # Motor Power String Formatation
                motors_power_packet = f"{manipulated_variable_1[kk]}\r"
               

                sendToArduino(arduinoData, motors_power_packet)
                
                # Store the output process values and control signal
                current_timestamp = datetime.datetime.now()
                process_output_sensor[str(current_timestamp)] = float(process_output[kk])
                control_signal_1[str(current_timestamp)] = float(manipulated_variable_1[kk])
                kk += 1

                percent_complete = kk / (samples_number)
                my_bar.progress(percent_complete, text=progress_text)

    # Turn off the motor
    sendToArduino(arduinoData, '0')

