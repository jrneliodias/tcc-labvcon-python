
from formatterInputs import *
from control.matlab import tf, c2d, tfdata
from numpy import exp, ones, zeros,arange,dot,convolve
from connections import *
import matplotlib.pyplot as plt


# Receber o objeto arduino da sessão
arduinoData = st.session_state.connected['arduinoData']


sampling_time = 0.01
samples_number = 2000

# Initial Conditions
angulo_sensor = zeros(samples_number)
angulo_model1 = zeros(samples_number)
angulo_model2 = zeros(samples_number)
erro1 = zeros(samples_number)
erro2 = zeros(samples_number)
d0barra1 = zeros(samples_number)
d0barra2 = zeros(samples_number)

# taumf1 e taumf2 Ajusts
ajuste1 = 1
ajuste2 = 1

# Setpoint
angulo_ref = 30*ones(samples_number)
angulo_ref[1000:] = 70

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

A_order = len(Am1)-1
B_order = len(Bm1) # Zero holder aumenta um grau

# Motor 2 Model Transfer Function
Gm2 = tf(Kpsmith2, [tausmith2, 1])
Gmz2 = c2d(Gm2, sampling_time)
num2, den2 = tfdata(Gmz2)
Bm2 = num2[0][0]
Am2 = den2[0][0]


# Close Loop Tau Calculation
tau_mf1 = ajuste1*tausmith1
alpha1 = exp(-sampling_time/tau_mf1)
alpha_delta_1 = [1,-alpha1]
B_delta_1 = convolve(Bm1,alpha_delta_1)

tau_mf2 = ajuste2*tausmith2
alpha2 = exp(-sampling_time/tau_mf2)
alpha_delta_2 = [1,-alpha2]
B_delta_2 = convolve(Bm2,alpha_delta_2)

# inicializar  o timer
start_time = time.time()
interation = 2

if st.button('Iniciar Simulação'):
    
    sendToArduino(arduinoData, '0,0')

    while interation < samples_number:
        current_time = time.time()
        if current_time - start_time > sampling_time:
            start_time = current_time
            # -----  Angle Sensor Output
            angulo_sensor[interation] = readFromArduino(arduinoData)

            # ---- Motor Model Output
            angulo_model1[interation] = dot(-Am1[1:], angulo_model1[interation-1:interation-A_order-1:-1]) + dot(Bm1,pot_motor_1[interation-1:interation-B_order-1:-1])
            angulo_model2[interation] =  dot(-Am2[1:], angulo_model2[interation-1:interation-A_order-1:-1]) - dot(Bm2,pot_motor_2[interation-1:interation-B_order-1:-1])

            # Determine uncertainty
            d0barra1[interation] =    angulo_sensor[interation] - angulo_model1[interation]
            d0barra2[interation] = - (angulo_sensor[interation] - angulo_model2[interation])

            # Determine Error
            erro1[interation] =    angulo_ref[interation] - d0barra1[interation]
            erro2[interation] = - (angulo_ref[interation] + d0barra2[interation])

            # Control Signal
            pot_motor_1[interation] = dot(-B_delta_1[1:],pot_motor_1[interation-1:interation-B_order-1:-1]) + (1-alpha1)*dot(Am1,erro1[interation:interation-A_order-1:-1])
            
            pot_motor_1[interation] = pot_motor_1[interation]/B_delta_1[0]

            pot_motor_2[interation] = dot(-B_delta_2[1:],pot_motor_2[interation-1:interation-B_order-1:-1]) + (1-alpha2)*dot(Am2,erro2[interation:interation-A_order-1:-1])
            
            pot_motor_2[interation] = pot_motor_2[interation]/B_delta_2[0]

            # Control Signal Saturation
            pot_motor_1[interation] = max(min_pot, min(pot_motor_1[interation], max_pot))
            pot_motor_2[interation] = max(min_pot, min(pot_motor_2[interation], max_pot))

            # Motor Power String Formatation
            motors_power_packet[interation] = f"{pot_motor_1[interation]},{pot_motor_2[interation]}\r"

            # Clean Sensor Data
            if angulo_sensor[interation] <= 0 or angulo_sensor[interation] > 90:
                angulo_sensor[interation] = angulo_sensor[interation-1]

            sendToArduino(arduinoData, motors_power_packet[interation])
            
            
            interation += 1


    sendToArduino(arduinoData, '0,0')

    ### Plotar os Resultados 

    time_interval = arange(0,samples_number*sampling_time,sampling_time)

    fig, ax = plt.subplots()
    ax.plot(time_interval, angulo_sensor,label='Resposta do sistema')
    ax.plot(time_interval, angulo_ref,linestyle='--',label='Referência')
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
    axes[0].plot(time_interval, pot_motor_1, label='Motor 1')
    axes[0].set_title('Sinal de Controle - Motor 1')
    axes[0].set_ylabel('PWM BW (%)')
    axes[0].set_xlabel('Tempo (s)')
    axes[0].set_ylim([6,16])

    # Plot data on the second subplot (right)
    axes[1].plot(time_interval, pot_motor_2, label='Motor 2', color='red')
    axes[1].set_title('Sinal de Controle - Motor 2')
    axes[1].set_ylabel('PWM BW (%)')
    axes[1].set_xlabel('Tempo (s)')
    axes[1].set_ylim([6,16])

    # Add legends to each subplot
    axes[0].legend()
    axes[1].legend()

    # Adjust layout
    st.pyplot(fig_control_signal,use_container_width=False)



