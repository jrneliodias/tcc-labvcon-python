

from control.matlab import tf, c2d, tfdata
import numpy as np
from connections import *
import matplotlib.pyplot as plt


# Receber o objeto arduino da sessão
arduinoData = st.session_state.connected['arduinoData']


sampling_time = 0.01
samples_number = 5000

# Initial Conditions
output_sensor = np.zeros(samples_number)
delta_control_signal = np.zeros(samples_number)


# Setpoint
reference = 50*np.ones(samples_number)
reference[4000:] = 70
q01 = 300

# Power Saturation
max_pot = 200
min_pot = -200

# Variável controlada
control_signal = np.zeros(samples_number)
motors_power_packet = ["0"]*samples_number

# Coefiientes do Modelo Smith motor 1
Kpsmith1 = 0.999 #7.737
thetasmith1 = 0.65
tausmith1 = 1.827 #0.6


# Motor 1 Model Transfer Function
#Gm1 = tf(Kpsmith1, [tausmith1, 1])
Gm1 = tf(1, [1, 2*0.9, 1]) # Second Order Transfer Function
Gmz1 = c2d(Gm1, sampling_time)
num1, den1 = tfdata(Gmz1)
Bm1 = num1[0][0]

"Bm1"
Bm1
Am1 = den1[0][0]
"Am1"
Am1
a1m1 = Am1[1]
st.write(f'a1m1 = {a1m1}')

b0m1 = Bm1[0]
st.write(f'b0m1 = {b0m1}')

A_order = len(Am1)-1
B_order = len(Bm1)-1 

# Coefiientes do Modelo Smith motor 2
# Kpsmith2 = 12.86
# thetasmith2 = 0.5
# tausmith2 = 0.66

# Motor 2 Model Transfer Function
# Gm2 = tf(Kpsmith2, [tausmith2, 1])
# Gmz2 = c2d(Gm2, sampling_time)
# num2, den2 = tfdata(Gmz2)
# Bm2 = num2[0][0]
# Am2 = den2[0][0]


# Determinar E(z^-1) e S(z^-1)
# na = 1;
# nb = 0;
# ns = na;
# ne = d-1;
# E(z^-1) = e0
# S(z^-1) = s0 + s1*z^-1

# Identidade Polinomial
# P(z^-1) = A(z^-1)Delta E(z^-1) + z^-d S(z^-1)
# P(z^-1) = 1


# Projeto do GMV motor 1

def create_P1_poly(ne,ns):
    P1 = np.zeros((ne + ns + 2,1))
    P1[0] = 1
    #P1[1] = -0.98
    return P1


def E_S_poly_calculation(ne,ns,Am1,P):
    delta = [1, -1]
    Am1_barra1 = np.convolve(Am1, delta)
    mat_Scoef1 = np.vstack((np.zeros((ne+1,ns+1)), np.eye(ns+1)))
    mat_EAcoef1= np.zeros((ne + ns + 2, ne+1))

    am1_barra_len = len(Am1_barra1)

    for k in range(ne+1):
        mat_EAcoef1[k:k+am1_barra_len,k] = Am1_barra1.T

    mat_SEcoef1 = np.concatenate((mat_EAcoef1,mat_Scoef1),axis=1)  

    mat_SEcoef1_inv = np.linalg.inv(mat_SEcoef1)
    EScoef1_array = np.dot(mat_SEcoef1_inv,P)


    epoly1 = EScoef1_array[0:ne1+1].T[0]
    spoly1 = EScoef1_array[ne1+1:].T[0]
    return epoly1,spoly1


# Calculo do polinômio R1(z^-1)
def r_poly_calculation(Bm1,epoly1,q0):
    BE_poly = np.convolve(Bm1,epoly1)
    BE_poly[0] += q0
    rpoly1 = BE_poly
    return rpoly1

d = 1
na1 = A_order
nb1 = B_order
ns1 = na1
ne1 = d-1


# Definir o polinômio P1(z)
P1 = create_P1_poly(ne1,ns1)
# Encontrar o polinômio E1(z) e S1(z)
e_poly_1,s_poly_1 = E_S_poly_calculation(ne1,ns1,Am1,P1)
"e_poly_1"
e_poly_1
"s_poly_1"
s_poly_1
"convolve(Bm1,e_poly_1)"
st.write(np.convolve(Bm1,e_poly_1))

# Encontrar o polinômio R por meio do Q1(z^-1) e B1(z^-1)
r_poly_1 = r_poly_calculation(Bm1,e_poly_1,q01)
"r_poly_1"
r_poly_1
nr1 = len(r_poly_1)-1

# Calculo do polinômio T1(z)
t01 = sum(P1)[0]

# Determinar E e S
e0 = 1
s0 = -(a1m1-1)*e0
st.write(f's0 = {s0}')
s1 = a1m1*e0
st.write(f's1 = {s1}')
r0 = b0m1+q01
st.write(f'r0 = {r0}')


# inicializar  o timer
start_time = time.time()
kk = 3

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

            # GMV Control Signal
            delta_control_signal[kk] = np.dot(r_poly_1[1:],delta_control_signal[kk-1:kk-nb1-1:-1]) + t01*reference[kk] - np.dot(s_poly_1,output_sensor[kk:kk-ns1-1:-1])
            delta_control_signal[kk]/=r_poly_1[0]
            
            #delta_control_signal[kk] = (t01*reference[kk] - (s0*output_sensor[kk] + s1*output_sensor[kk-1]))/r0
            #  deltaU(k) = (-r1/r0)*deltaU(k-1) + (t0/r0)*ref(k) - (s0/r0)*y(k) -(s1/r0)*y(k-1)-(s2/r0)*y(k-2);
            control_signal[kk] = control_signal[kk-1] +  delta_control_signal[kk]
            
            # Control Signal Saturation
            control_signal[kk] = max(min_pot, min(control_signal[kk], max_pot))

            # Motor Power String Formatation
            motors_power_packet[kk] = f"{control_signal[kk]}\r"

            # Clean Sensor Data
            if output_sensor[kk] <= 0 or output_sensor[kk] > 90:
                output_sensor[kk] = output_sensor[kk-1]

            sendToArduino(arduinoData, motors_power_packet[kk])
            
            kk += 1
            percent_complete = kk / (samples_number)
            my_bar.progress(percent_complete, text=progress_text)


    sendToArduino(arduinoData, '0')

    ### Plotar os Resultados 

    time_interval = np.arange(0,samples_number*sampling_time,sampling_time)

    fig, ax = plt.subplots()
    ax.plot(time_interval, output_sensor,label='Resposta do sistema')
    ax.plot(time_interval, reference,linestyle='--',label='Referência')
    ax.legend()
    ax.set_xlabel('Tempo (s)')
    ax.set_ylabel('Ângulo (º)')
    ax.set_title('Resposta do Sistema')
    ax.set_ylim([0,90])

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



