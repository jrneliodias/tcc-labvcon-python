

from control.matlab import tf, c2d, tfdata
import numpy as np
from connections import *
import matplotlib.pyplot as plt
from controllers_process.gpc_controller_process import GeneralizedPredictiveController
from mainSideBar import *


##########################################################################

# SideBar
with st.sidebar:
    mainSidebarMenu()
    with st.expander("Session States:"):
        st.session_state

##########################################################################

# Receber o objeto arduino da sessão
if 'arduinoData' in st.session_state.connected:
    arduinoData = st.session_state.connected['arduinoData']
else:
    st.warning('Arduino não conectado')

Ny_1 = 90
Nu_1 = 1
lambda_1 = 200
Ny_2 = 90
Nu_2 = 1
lambda_2 = 200
sampling_time = 0.01
samples_number = 3000

# Initial Conditions
output_sensor = np.zeros(samples_number)
delta_control_signal_1 = np.zeros(samples_number)
delta_control_signal_2 = np.zeros(samples_number)

model_output_1 = np.zeros(samples_number)

# Setpoint
reference_input = 30*np.ones(samples_number+Ny_1)
reference_input[1000:] = 50
reference_input[2000:] = 70

# Power Saturation
# max_pot = 2000
# min_pot = -2000
max_pot = 15
min_pot = 7

# Variável controlada
control_signal_1 = np.zeros(samples_number)
control_signal_2 = np.zeros(samples_number)
serial_data_pack = "0,0"
# #Gm1 = tf(0.8, [1, 2*0.3, 1]) # Second Order Transfer Function
# alfa = 0.9
# Bm1filter motor 1 
# [0.12788, -0.11509]

# Am1 discreto
# [1, -0.9835]

# Bm1filter motor 2
# [0.193379, -0.1740418]

# Am2 discreto
# [1, -0.985]

# Ny_11 = Ny_12 = 80

# lambda1 = 200

# Coefiientes do Modelo 1º Ordem Virtual Arduino
# Kpsmith1 =  0.999 
# thetasmith1 = 0.65 
# tausmith1 = 1.827 

# # Coefiientes do Modelo Smith motor 1
Kpsmith1 =  7.737 
thetasmith1 = 0.65 
tausmith1 =  0.6


# Motor 1 Model Transfer Function
Gm1 = tf(Kpsmith1, [tausmith1, 1])
Gmz1 = c2d(Gm1, sampling_time)
num1, den1 = tfdata(Gmz1)
Bm1 = num1[0][0]
Am1 = den1[0][0]
# Bm1 = np.array([0.5,-0.8])

# Coefiientes do Modelo Smith motor 2
Kpsmith2 =  12.86 
thetasmith2 = 0.65 
tausmith2 =  0.66


# Motor 2 Model Transfer Function
Gm2 = tf(Kpsmith2, [tausmith2, 1])
Gmz2 = c2d(Gm2, sampling_time)
num2, den2 = tfdata(Gmz2)
Bm2 = num2[0][0]
Am2 = den2[0][0]
# Bm1 = np.array([0.5,-0.8])


"Bm1"
Bm1
# Am1 = np.array([1,-3,2])
"Am1"
Am1
a1m1 = Am1[1]
st.write(f'a1m1 = {a1m1}')

b0m1 = Bm1[0]
st.write(f'b0m1 = {b0m1}')

K_alpha = 0.1
alpha = 0.9
alpha_filter = np.array([1,-alpha])
Bm1_filter = np.convolve(K_alpha*alpha_filter,Bm1)
'Bm1_filter'
Bm1_filter
Bm2_filter = np.convolve(K_alpha*alpha_filter,Bm2)
'Bm2_filter'
Bm2_filter


A_order = len(Am1)-1
B_order = len(Bm1)

# GPC CONTROLLER
gpc_m1 = GeneralizedPredictiveController(nit= samples_number,Ny=Ny_1,Nu=Nu_1,lambda_=lambda_1,ts=sampling_time,Am=Am1, Bm=Bm1_filter)
gpc_m2 = GeneralizedPredictiveController(nit= samples_number,Ny=Ny_2,Nu=Nu_2,lambda_=lambda_2,ts=sampling_time,Am=Am2, Bm=Bm2_filter)
gpc_m1.calculateController()
gpc_m2.calculateController()
st.write(vars(gpc_m1))
st.write(vars(gpc_m2))



# inicializar  o timer
start_time = time.time()
kk = 4

future_inputs = 1

## ---- Cáculo dos elementos do sinal de controle R, S e T
T_1 = sum(gpc_m1.Kgpc);                       # polinômio que afeta o sinal de entrada
S_1 = np.dot(gpc_m1.Kgpc,gpc_m1.F);           # polinômio que afeta as saída preditas
R_1 = np.dot(gpc_m1.Kgpc,gpc_m1.H);           # polinômio que afeta a ação de controle passada du(t-1);
R_1 = np.insert(R_1,0,1)
T_2 = sum(gpc_m2.Kgpc);                       # polinômio que afeta o sinal de entrada
S_2 = np.dot(gpc_m2.Kgpc,gpc_m2.F);           # polinômio que afeta as saída preditas
R_2 = np.dot(gpc_m2.Kgpc,gpc_m2.H);           # polinômio que afeta a ação de controle passada du(t-1);
R_2 = np.insert(R_2,0,1)
# st.write(R)

if st.button('Iniciar Simulação'):
    # Inicializar a barra de progresso
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)
    
    sendToArduino(arduinoData, '0,0')

    ###### PID GPC SISO
    # while kk < samples_number:
    #     current_time = time.time()
    #     if current_time - start_time > sampling_time:
    #         start_time = current_time
    #         # -----  Angle Sensor Output
    #         output_sensor[kk] = readFromArduino(arduinoData)
            
    #         #output_sensor[kk] = np.dot(-Am1[1:],output_sensor[kk-1:kk-A_order-1:-1]) + np.dot(Bm1,control_signal[kk-1:kk-B_order-1:-1])       
                       
    #         if future_inputs == 0:
    #             #  Referência futura desconhecida
    #             aux_ref = reference_input[kk]*np.ones(Ny_1)
    #         elif future_inputs == 1:
    #             # Referência futura conhecida
    #             aux_ref = reference_input[kk:kk+Ny_1]
    #             #st.write(aux_ref)
            
    #         F_yf = np.dot(gpc_m1.F,output_sensor[kk:kk-A_order-1:-1])
    #         # st.write('F*yf',F_yf)
            
    #         H_du = np.dot(gpc_m1.H,delta_control_signal[kk-1])
    #         # st.write('H*du',H_du)
            
    #         fi = np.squeeze(H_du) + F_yf
    #         # st.write('fi',fi)
    #         # st.write('fi',fi)
    #         # st.write('gpc_m1.Kgpc',gpc_m1.Kgpc)
    #         # st.write('aux_ref',aux_ref)
    #         # st.write('fi',fi)
    #         # st.write('aux_ref',aux_ref.shape)
    #         # st.write('fi',fi.shape)
    #         delta_control_signal[kk] = np.dot(gpc_m1.Kgpc,(aux_ref-fi))
            
    #         # Controle via estrutura RST
    #         #delta_control_signal[kk] = -R[1]*delta_control_signal[kk-1] + T*reference_input[kk] - np.dot(S,output_sensor[kk:kk-A_order-1:-1])
            
    #         # st.write('delta_control_signal',delta_control_signal)
            
    #         control_signal[kk] = control_signal[kk-1] + delta_control_signal[kk]
                        
    #         # Control Signal Saturation
    #         control_signal[kk] = max(min_pot, min(control_signal[kk], max_pot))

    #         # Motor Power String Formatation
    #         motors_power_packet[kk] = f"{control_signal[kk]}\r"

    #         # # Clean Sensor Data
    #         # if output_sensor[kk] <= 0 or output_sensor[kk] > 90:
    #         #     output_sensor[kk] = output_sensor[kk-1]

    #         sendToArduino(arduinoData, motors_power_packet[kk])
            
    #         kk += 1
    #         percent_complete = kk / (samples_number)
    #         my_bar.progress(percent_complete, text=progress_text)
   
    
    ###### PID GPC AVIAO       
    while kk < samples_number:
        current_time = time.time()
        if current_time - start_time > sampling_time:
            start_time = current_time
            # -----  Angle Sensor Output
            output_sensor[kk] = readFromArduino(arduinoData)
            
            #output_sensor[kk] = np.dot(-Am1[1:],output_sensor[kk-1:kk-A_order-1:-1]) + np.dot(Bm1,control_signal[kk-1:kk-B_order-1:-1])       
         
            # Controle via estrutura RST
            delta_control_signal_1[kk] = -R_1[1]*delta_control_signal_1[kk-1] + T_1*reference_input[kk] - np.dot(S_1,output_sensor[kk:kk-A_order-1:-1])
            
            control_signal_1[kk] = control_signal_1[kk-1] + delta_control_signal_1[kk]
            
            delta_control_signal_2[kk] = -R_2[1]*delta_control_signal_2[kk-1] + T_2*reference_input[kk] - np.dot(S_2,output_sensor[kk:kk-A_order-1:-1])
            control_signal_2[kk] = control_signal_2[kk-1] - delta_control_signal_2[kk]
            
            # Control Signal Saturation
            control_signal_1[kk] = max(min_pot, min(control_signal_1[kk], max_pot))
        
            control_signal_2[kk] = max(min_pot, min(control_signal_2[kk], max_pot))
        

            # Motor Power String Formatation
            serial_data_pack = f"{control_signal_1[kk]},{control_signal_2[kk]}\r"
            sendToArduino(arduinoData, serial_data_pack)
                
            
            kk += 1
            percent_complete = kk / (samples_number)
            my_bar.progress(percent_complete, text=progress_text)

    
    # # # GPC AVIAO       
    # while kk < samples_number:
    #     current_time = time.time()
    #     if current_time - start_time > sampling_time:
    #         start_time = current_time
    #         # -----  Angle Sensor Output
    #         output_sensor[kk] = readFromArduino(arduinoData)
            
    #         #output_sensor[kk] = np.dot(-Am1[1:],output_sensor[kk-1:kk-A_order-1:-1]) + np.dot(Bm1,control_signal[kk-1:kk-B_order-1:-1])       
         
            
    #         F_yf_1 = np.dot(gpc_m1.F,output_sensor[kk:kk-A_order-1:-1])
    #         F_yf_2 = np.dot(gpc_m2.F,output_sensor[kk:kk-A_order-1:-1])
    #         # st.write('F*yf',F_yf)
            
                        
    #         if future_inputs == 0:
    #              #  Referência futura desconhecida
    #              aux_ref_1 = reference_input[kk]*np.ones(Ny_1)
    #              aux_ref_2 = reference_input[kk]*np.ones(Ny_2)
    #         elif future_inputs == 1:
    #              # Referência futura conhecida
    #              aux_ref_1 = reference_input[kk:kk+Ny_1]
    #              aux_ref_2 = reference_input[kk:kk+Ny_2]
  
                
    #         H_du_1 = np.dot(gpc_m1.H,delta_control_signal_1[kk-1])
    #         H_du_2 = np.dot(gpc_m2.H,delta_control_signal_2[kk-1])
    #             # st.write('H*du',H_du)
                
    #         fi_1 = np.squeeze(H_du_1) + F_yf_1
    #         fi_2 = np.squeeze(H_du_2) + F_yf_2
            
    #         delta_control_signal_1[kk] = np.dot(gpc_m1.Kgpc,(aux_ref_1-fi_1))
    #         control_signal_1[kk] = control_signal_1[kk-1] + delta_control_signal_1[kk]
            
    #         delta_control_signal_2[kk] = np.dot(gpc_m2.Kgpc,(aux_ref_2-fi_2))
    #         control_signal_2[kk] = control_signal_2[kk-1] - delta_control_signal_2[kk]
            
    #         # Control Signal Saturation
    #         control_signal_1[kk] = max(min_pot, min(control_signal_1[kk], max_pot))
        
    #         control_signal_2[kk] = max(min_pot, min(control_signal_2[kk], max_pot))
        

    #         # Motor Power String Formatation
    #         serial_data_pack = f"{control_signal_1[kk]},{control_signal_2[kk]}\r"
    #         sendToArduino(arduinoData, serial_data_pack)
                
            
    #         kk += 1
    #         percent_complete = kk / (samples_number)
    #         my_bar.progress(percent_complete, text=progress_text)

    
    sendToArduino(arduinoData, '0,0')

    ### Plotar os Resultados 

    time_interval = np.arange(0,samples_number*sampling_time,sampling_time)

    fig, ax = plt.subplots()
    ax.plot(time_interval, output_sensor,label='Resposta do sistema')
    ax.plot(time_interval, reference_input[0:samples_number],linestyle='--',label='Referência')
    ax.legend()
    ax.set_xlabel('Tempo (s)')
    ax.set_ylabel('Ângulo (º)')
    ax.set_title('Resposta do Sistema')
    # ax.set_ylim([0,90])
    ax.grid()

    # Display the Matplotlib figure within Streamlit
    st.pyplot(fig, use_container_width=False)


    # Create a figure with two subplots
    fig_control_signal, axes = plt.subplots(nrows=2, ncols=1)
    plt.subplots_adjust(hspace=0.8)  # Increase the horizontal spacing
    # Plot data on the first subplot (left)
    axes[0].plot(time_interval, control_signal_1, label='Motor 1')
    axes[0].set_title('Sinal de Controle - Motor 1')
    axes[0].set_ylabel('PWM BW (%)')
    axes[0].set_xlabel('Tempo (s)')
    #axes[0].set_ylim([6,16])

    # Plot data on the second subplot (right)
    axes[1].plot(time_interval, control_signal_2, label='Motor 2', color='red')
    axes[1].set_title('Sinal de Controle - Motor 2')
    axes[1].set_ylabel('PWM BW (%)')
    axes[1].set_xlabel('Tempo (s)')
    #axes[1].set_ylim([6,16])

    # Add legends to each subplot
    axes[0].legend()
    axes[1].legend()

    # Adjust layout
    st.pyplot(fig_control_signal,use_container_width=False)



def future_inputs_selection(future_inputs_checkbox,kk,Ny_1,reference_input):
    if future_inputs_checkbox:
    # Referência futura conhecidax
        aux_ref = reference_input[kk:kk+Ny_1]
    else:
    #  Referência futura desconhecida
        aux_ref = reference_input[kk]*np.ones(Ny_1)
        
    return aux_ref
