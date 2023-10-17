import streamlit as st
from formatterInputs import *
import numpy as np
from connections import *
import datetime
from session_state import get_session_variable
from controllers_process.validations_functions import *


class GeneralizedPredictiveController:
    def __init__(self,nit, Ny,Nu,lambda_,ts,Am,Bm) -> None:
        self.nit = nit
        self.Ny = Ny
        self.Nu = Nu
        self.lambda_ = lambda_
        self.ts = ts
        self.Am = Am
        self.Bm = Bm
        na = len(Am)-1
        self.E = np.zeros((Ny,Ny))
        self.G = np.zeros((Ny,Nu))
        self.H = np.zeros((Ny,1))  
        self.gt = np.zeros((Ny,Ny))  
        self.Kgpc = np.zeros((1,Ny))  
        self.F = np.zeros((Ny,na+1))
    
    def calculateController(self):
        ny = self.Ny
        nu = self.Nu
        delta = [1,-1]
        Atil = np.convolve(self.Am,delta)
        # st.write('Atil',Atil)
        natil = len(Atil)
        nb = len(self.Bm) - 1  
        G_aux = np.zeros(ny)
        
        # Calculate the predictor matrices (F, H, G)
        # Diophantine Fist Equation
        #rr = np.concatenate((1, np.zeros(natil - 1)))
        rr = np.ones(natil)
        rr[1:] = 0
        # st.write('rr =')
        # st.write(rr)
        q = np.zeros(ny)
        
        # st.write('q =',q)
    
        
        
        for k in range(ny):
            q[k],r = np.polydiv(rr,Atil)
            #st.write('new r =' ,r)
            self.F[k,:] = r
            rr = np.append(r,0)
            #st.write('new rr =' ,rr)
        
        st.write('q =' ,q)
                
        for j in range(ny):
            self.E[j:,j] = q[j]
                
        # st.write('E =' ,self.E)
                
        # # Diophantine Second Equation
        B_aux = np.convolve(self.Bm,self.E[-1])
        # st.write('Baux =' ,B_aux)
        nb_aux =len(B_aux)
        T_BE = np.zeros(nb_aux+1)
        T_BE[0] = 1
        # st.write('T_BE =' ,T_BE)
        
        
        rr_BE = B_aux
        
        for k in range(ny):
            rr_BE = np.append(rr_BE,0)
            q_BE,r_BE = np.polydiv(rr_BE, T_BE)
            G_aux[k] = q_BE
            rr_BE = r_BE
        
        
        
        # st.write('q_BE =' ,q_BE)
        # st.write('r_BE =' ,r_BE)
        # st.write('G_aux =' ,G_aux)
        
        
        for i in range(nu):
            for j in range(i,ny):
                self.G[j][i] = G_aux[j-i]
        
        # st.write('G =' ,self.G)
        
        # Matriz auxiliar para multiplica com E e obter H
        Bm_aux = np.array(ny)
        #Bm_aux[0:nb+1] = self.Bm
        #np.convolve(self.E,self.Bm) 
        
        # Haux = np.zeros((ny,nb))
        for i in range(ny):
            EB_conv = np.convolve(self.E[i,0:(i+1)],self.Bm)    # B*E + j^{-1}*H
            #st.write('EB_conv',EB_conv)
            self.H[i] = EB_conv[-1]
            #st.write('H',self.H)
            
      
        # for i in range(ny):
        #     self.H[i] = Haux[i][i+1:i+1+nb]
        
        G = self.G
        lambda_ = self.lambda_
        
        G_lambda_op = np.dot(G.T,G) + lambda_ *np.eye(nu) # G^T * G + lambda*I
        # st.write('G_lambda_op',G_lambda_op)
        G_lambda_op_inv = np.linalg.inv(G_lambda_op) # (G^T * G + lambda*I)^{-1}
        self.gt = np.dot(G_lambda_op_inv, G.T) # (G^T * G + lambda*I)^{-1} * G^{T}
        
        self.Kgpc = self.gt[0]
                
                
                
                
                
                
                
def gpcControlProcessSISO(transfer_function_type:str,num_coeff:str,den_coeff:str,
                          gpc_q01:float, 
                          gpc_multiple_reference1:float, gpc_multiple_reference2:float, gpc_multiple_reference3:float,
                          change_ref_instant2 = 1, change_ref_instant3 = 1):
    
    if num_coeff == '':
        return st.error('Coeficientes incorretos no Numerador.')
    
    if den_coeff =='':
        return st.error('Coeficientes incorretos no Denominador.')

    # Receber os valores de tempo de amostragem e número de amostras da sessão
    sampling_time = get_session_variable('sampling_time')
    samples_number = get_session_variable('samples_number')
    
    if 'arduinoData' not in st.session_state.connected:
        return st.warning('Arduino não conectado!')
    
    # Receber o objeto arduino da sessão
    arduinoData = st.session_state.connected['arduinoData']

    # gpc Controller Project

    # Initial Conditions
    process_output = np.zeros(samples_number)
    delta_control_signal = np.zeros(samples_number)

    # Take the index of time to change the referencee
    instant_sample_2 = get_sample_position(sampling_time, samples_number, change_ref_instant2)
    instant_sample_3 = get_sample_position(sampling_time, samples_number, change_ref_instant3)

    reference_input = gpc_multiple_reference1*np.ones(samples_number)
    reference_input[instant_sample_2:instant_sample_3] = gpc_multiple_reference2
    reference_input[instant_sample_3:] = gpc_multiple_reference3
    
    st.session_state.controller_parameters['reference_input'] = reference_input.tolist()

    # Power Saturation
    max_pot = get_session_variable('saturation_max_value')
    min_pot = get_session_variable('saturation_min_value')

    # Manipulated variable
    manipulated_variable_1 = np.zeros(samples_number)
    serial_data_pack = "0"

    # Model transfer Function
    A_coeff, B_coeff = convert_tf_2_discrete(num_coeff,den_coeff,transfer_function_type)
    
    # print(A_coeff)
    # print(B_coeff)
    A_order = len(A_coeff)-1
    B_order = len(B_coeff)-1 
    # Close Loop Tau Calculation
    # tau_mf1 = ajuste1*tausmith1
    q01 = gpc_q01
    
  
    

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
                current_timestamp = datetime.now()
                process_output_sensor[str(current_timestamp)] = float(process_output[kk])
                control_signal_1[str(current_timestamp)] = float(manipulated_variable_1[kk])
                kk += 1

                percent_complete = kk / (samples_number)
                my_bar.progress(percent_complete, text=progress_text)
                
                sendToArduino(arduinoData, '0')
                

            # ---- Motor Model Output
            elif kk == 1 and A_order == 1:
              
                # Control Signal Saturation
                manipulated_variable_1[kk] = max(min_pot, min(manipulated_variable_1[kk], max_pot))
            

                # Motor Power String Formatation
                serial_data_pack = f"{manipulated_variable_1[kk]}\r"

                sendToArduino(arduinoData, serial_data_pack)
                
                # Store the output process values and control signal
                current_timestamp = datetime.datetime.now()
                process_output_sensor[str(current_timestamp)] = float(process_output[kk])
                control_signal_1[str(current_timestamp)] = float(manipulated_variable_1[kk])
                kk += 1

                percent_complete = kk / (samples_number)
                my_bar.progress(percent_complete, text=progress_text)
                                        
            elif kk >A_order:
                
              
                
                # Control Signal Saturation
                manipulated_variable_1[kk] = max(min_pot, min(manipulated_variable_1[kk], max_pot))
            

                # Motor Power String Formatation
                serial_data_pack = f"{manipulated_variable_1[kk]}\r"
                sendToArduino(arduinoData, serial_data_pack)
                
                # Store the output process values and control signal
                current_timestamp = datetime.now()
                process_output_sensor[str(current_timestamp)] = float(process_output[kk])
                control_signal_1[str(current_timestamp)] = float(manipulated_variable_1[kk])
                kk += 1

                percent_complete = kk / (samples_number)
                my_bar.progress(percent_complete, text=progress_text)

    # Turn off the motor
    sendToArduino(arduinoData, '0')


def gpcControlProcessTISO(transfer_function_type:str,num_coeff_1:str,den_coeff_1:str, num_coeff_2:str,den_coeff_2:str,
                          gpc_q01:float,gpc_q02:float,
                          gpc_multiple_reference1:float, gpc_multiple_reference2:float, gpc_multiple_reference3:float,
                          change_ref_instant2 = 1, change_ref_instant3 = 1):

    if num_coeff_1 == '':
        return st.error('Coeficientes incorretos no Numerador 1.')
    
    if den_coeff_1 =='':
        return st.error('Coeficientes incorretos no Denominador 1.')
    
    if num_coeff_2 == '':
        return st.error('Coeficientes incorretos no Numerador 2.')
    
    if den_coeff_2 =='':
        return st.error('Coeficientes incorretos no Denominador 2.')

    # Receber os valores de tempo de amostragem e número de amostras da sessão
    sampling_time = get_session_variable('sampling_time')
    samples_number = get_session_variable('samples_number')

    if not st.session_state.connected['arduinoData']:
        return st.toast('Arduino não conectado!')
    # Receber o objeto arduino da sessão
    arduinoData = st.session_state.connected['arduinoData']
    
    # gpc Controller Project

    # Initial Conditions
    process_output = np.zeros(samples_number)
    delta_control_signal_1 = np.zeros(samples_number)
    delta_control_signal_2 = np.zeros(samples_number)

    # Take the index of time to change the referencee
    instant_sample_2 = get_sample_position(sampling_time, samples_number, change_ref_instant2)
    instant_sample_3 = get_sample_position(sampling_time, samples_number, change_ref_instant3)

    reference_input = gpc_multiple_reference1*np.ones(samples_number)
    reference_input[instant_sample_2:instant_sample_3] = gpc_multiple_reference2
    reference_input[instant_sample_3:] = gpc_multiple_reference3
    st.session_state.controller_parameters['reference_input'] = reference_input.tolist()


    # Power Saturation
    max_pot = get_session_variable('saturation_max_value')
    min_pot = get_session_variable('saturation_min_value')


    # Manipulated variable
    manipulated_variable_1 = np.zeros(samples_number)
    manipulated_variable_2 = np.zeros(samples_number)
    motors_power_packet = "0,0"

    # Model transfer Function 1
    A_coeff_1, B_coeff_1 = convert_tf_2_discrete(num_coeff_1,den_coeff_1,transfer_function_type)
    
    # print(A_coeff)
    # print(B_coeff)
    A_order = len(A_coeff_1)-1
    B_order = len(B_coeff_1)-1 # Zero holder aumenta um grau

    ## Model transfer Function 2
    A_coeff_2, B_coeff_2 = convert_tf_2_discrete(num_coeff_2,den_coeff_2,transfer_function_type)
    q01 = gpc_q01
    q02 = gpc_q02
    
    # print(A_coeff)
    # print(B_coeff)
    d = 1
    na1 = A_order
    nb1 = B_order
    ns1 = na1
    ne1 = d-1
    

    
    # clear previous control signal values
    st.session_state.controller_parameters['control_signal_1']= dict()
    control_signal_1 = st.session_state.controller_parameters['control_signal_1']
    
    
    # clear previous control signal values
    st.session_state.controller_parameters['control_signal_2']= dict()
    control_signal_2 = st.session_state.controller_parameters['control_signal_2']
    
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
    sendToArduino(arduinoData, '0,0')

    while kk < samples_number:
        current_time = time.time()
        if current_time - start_time > sampling_time:
            start_time = current_time
            
            # -----  Angle Sensor Output
            process_output[kk] = readFromArduino(arduinoData)
            
            if kk <= A_order:
                # Store the output process values and control signal
                current_timestamp = datetime.now()
                process_output_sensor[str(current_timestamp)] = float(process_output[kk])
                control_signal_1[str(current_timestamp)] = float(manipulated_variable_1[kk])
                control_signal_2[str(current_timestamp)] = float(manipulated_variable_2[kk])
                kk += 1

                percent_complete = kk / (samples_number)
                my_bar.progress(percent_complete, text=progress_text)
                
                sendToArduino(arduinoData, '0,0')
                
            # ---- Motor Model Output
            elif kk == 1 and A_order == 1:
              
                manipulated_variable_2[kk] = manipulated_variable_2[kk-1] -  delta_control_signal_2[kk]
               
                # Control Signal Saturation
                manipulated_variable_1[kk] = max(min_pot, min(manipulated_variable_1[kk], max_pot))
                manipulated_variable_2[kk] = max(min_pot, min(manipulated_variable_2[kk], max_pot))
            

                # Motor Power String Formatation
                motors_power_packet = f"{manipulated_variable_1[kk]},{manipulated_variable_2[kk]}\r"

                sendToArduino(arduinoData, motors_power_packet)
                
                # Store the output process values and control signal
                current_timestamp = datetime.now()
                process_output_sensor[str(current_timestamp)] = float(process_output[kk])
                control_signal_1[str(current_timestamp)] = float(manipulated_variable_1[kk])
                control_signal_2[str(current_timestamp)] = float(manipulated_variable_2[kk])
                kk += 1

                percent_complete = kk / (samples_number)
                my_bar.progress(percent_complete, text=progress_text)
                
            elif kk > A_order:
                
                # gpc Control Signal
              
                # Control Signal
                manipulated_variable_1[kk] = manipulated_variable_1[kk-1] +  delta_control_signal_1[kk]
                manipulated_variable_2[kk] = manipulated_variable_2[kk-1] -  delta_control_signal_2[kk]
                
               
                # Control Signal Saturation
                manipulated_variable_1[kk] = max(min_pot, min(manipulated_variable_1[kk], max_pot))
                manipulated_variable_2[kk] = max(min_pot, min(manipulated_variable_2[kk], max_pot))
            

                # Motor Power String Formatation
                motors_power_packet = f"{manipulated_variable_1[kk]},{manipulated_variable_2[kk]}\r"

                sendToArduino(arduinoData, motors_power_packet)
                
                # Store the output process values and control signal
                current_timestamp = datetime.now()
                process_output_sensor[str(current_timestamp)] = float(process_output[kk])
                control_signal_1[str(current_timestamp)] = float(manipulated_variable_1[kk])
                control_signal_2[str(current_timestamp)] = float(manipulated_variable_2[kk])
                kk += 1

                percent_complete = kk / (samples_number)
                my_bar.progress(percent_complete, text=progress_text)
                
                


    # Turn off the motor
    sendToArduino(arduinoData, '0,0')

