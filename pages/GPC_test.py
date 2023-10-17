

from control.matlab import tf, c2d, tfdata
import numpy as np
from connections import *
import matplotlib.pyplot as plt
from controllers_process.gpc_controller_process import GeneralizedPredictiveController


# Receber o objeto arduino da sessão
if 'arduinoData' in st.session_state.connected:
    arduinoData = st.session_state.connected['arduinoData']
else:
    st.warning('Arduino não conectado')
     
Ny = 3
Nu = 1
lambda_ = 2
sampling_time = 0.1
samples_number = 500

# Initial Conditions
output_sensor = np.zeros(samples_number)
delta_control_signal = np.zeros(samples_number)

model_output_1 = np.zeros(samples_number)

# Setpoint
reference = 50*np.ones(samples_number+Ny)
# reference[1000:] = 70

# Power Saturation
max_pot = 2000
min_pot = -2000

# Variável controlada
control_signal = np.zeros(samples_number)
motors_power_packet = ["0"]*samples_number

# Coefiientes do Modelo Smith motor 1
Kpsmith1 = 0.999 #7.737
thetasmith1 = 0.65
tausmith1 = 1.827 #0.6


# Motor 1 Model Transfer Function
Gm1 = tf(Kpsmith1, [tausmith1, 1])
# Gm1 = tf(0.8, [1, 2*0.3, 1]) # Second Order Transfer Function
Gmz1 = c2d(Gm1, sampling_time)
num1, den1 = tfdata(Gmz1)
Bm1 = num1[0][0]
# Bm1 = np.array([0.5,-0.8])

"Bm1"
Bm1
Am1 = den1[0][0]
# Am1 = np.array([1,-3,2])
"Am1"
Am1
a1m1 = Am1[1]
st.write(f'a1m1 = {a1m1}')

b0m1 = Bm1[0]
st.write(f'b0m1 = {b0m1}')

A_order = len(Am1)-1
B_order = len(Bm1)

# GPC CONTROLLER
gpc_m1 = GeneralizedPredictiveController(nit= samples_number,Ny=Ny,Nu=Nu,lambda_=lambda_,ts=sampling_time,Am=Am1, Bm=Bm1)
gpc_m1.calculateController()
#st.write(vars(gpc_m1))



# inicializar  o timer
start_time = time.time()
kk = 4

future_inputs = 1

if st.button('Iniciar Simulação'):
    # Inicializar a barra de progresso
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)
    
    sendToArduino(arduinoData, '0')

    while kk < samples_number:
        current_time = time.time()
        if current_time - start_time > sampling_time:
            start_time = current_time
            # -----  Angle Sensor Output
            output_sensor[kk] = readFromArduino(arduinoData)
            
            #output_sensor[kk] = np.dot(-Am1[1:],output_sensor[kk-1:kk-A_order-1:-1]) + np.dot(Bm1,control_signal[kk-1:kk-B_order-1:-1])       
                       
            if future_inputs == 0:
                #  Referência futura desconhecida
                aux_ref = reference[kk]*np.ones(Ny)
            elif future_inputs == 1:
                # Referência futura conhecida
                aux_ref = reference[kk:kk+Ny]
                #st.write(aux_ref)
            
            F_yf = np.dot(gpc_m1.F,output_sensor[kk:kk-A_order-1:-1])
            # st.write('F*yf',F_yf)
            
            H_du = np.dot(gpc_m1.H,delta_control_signal[kk-1])
            # st.write('H*du',H_du)
            
            fi = np.squeeze(H_du) + F_yf
            # st.write('fi',fi)
            # st.write('fi',fi)
            # st.write('gpc_m1.Kgpc',gpc_m1.Kgpc)
            # st.write('aux_ref',aux_ref)
            # st.write('fi',fi)
            # st.write('aux_ref',aux_ref.shape)
            # st.write('fi',fi.shape)
            delta_control_signal[kk] = np.dot(gpc_m1.Kgpc,(aux_ref-fi))
            
            # st.write('delta_control_signal',delta_control_signal)
            
            control_signal[kk] = control_signal[kk-1] + delta_control_signal[kk]
                        
            # Control Signal Saturation
            control_signal[kk] = max(min_pot, min(control_signal[kk], max_pot))

            # Motor Power String Formatation
            motors_power_packet[kk] = f"{control_signal[kk]}\r"

            # # Clean Sensor Data
            # if output_sensor[kk] <= 0 or output_sensor[kk] > 90:
            #     output_sensor[kk] = output_sensor[kk-1]

            sendToArduino(arduinoData, motors_power_packet[kk])
            
            kk += 1
            percent_complete = kk / (samples_number)
            my_bar.progress(percent_complete, text=progress_text)

    
    sendToArduino(arduinoData, '0')

    ### Plotar os Resultados 

    time_interval = np.arange(0,samples_number*sampling_time,sampling_time)

    fig, ax = plt.subplots()
    ax.plot(time_interval, output_sensor,label='Resposta do sistema')
    ax.plot(time_interval, reference[0:samples_number],linestyle='--',label='Referência')
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
    axes[0].plot(time_interval, control_signal, label='Motor 1')
    axes[0].set_title('Sinal de Controle - Motor 1')
    axes[0].set_ylabel('PWM BW (%)')
    axes[0].set_xlabel('Tempo (s)')
    #axes[0].set_ylim([6,16])

    # Plot data on the second subplot (right)
    axes[1].plot(time_interval, control_signal, label='Motor 2', color='red')
    axes[1].set_title('Sinal de Controle - Motor 2')
    axes[1].set_ylabel('PWM BW (%)')
    axes[1].set_xlabel('Tempo (s)')
    #axes[1].set_ylim([6,16])

    # Add legends to each subplot
    axes[0].legend()
    axes[1].legend()

    # Adjust layout
    st.pyplot(fig_control_signal,use_container_width=False)



