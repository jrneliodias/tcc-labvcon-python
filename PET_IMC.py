
from formatterInputs import *
from control.matlab import tf, c2d, tfdata
from numpy import exp, ones, zeros,arange,ceil
from connections import *
import matplotlib.pyplot as plt


# Receber o objeto arduino da sessão
commPort ='COM9'
baudrate = 9600
arduinoData = connectSerialManual(commPort,baudrate)

motor_calibration = input('Continuar? ')


sampling_time = 0.1
samples_number = 2000

# Initial Conditions
temperature_sensor = zeros(samples_number)
heater_model = zeros(samples_number)
angulo_model2 = zeros(samples_number)
erro1 = zeros(samples_number)
erro2 = zeros(samples_number)
d0barra1 = zeros(samples_number)
d0barra2 = zeros(samples_number)

# taumf1 e taumf2 Ajusts
ajuste1 = 0.6
ajuste2 = 0.6

# Setpoint
temperature_ref = 150*ones(samples_number)
#temperature_ref[1000:] = 70

# Power Saturation

max_pot = 15
min_pot = 7

# Variável controlada
control_signal = zeros(samples_number)

motors_power_packet = ["0"]*samples_number

# Coeficientes do Modelo Smith motor 1
Kp = 2.38
theta = 4.32
tau = 199


# Heater Model Transfer Function
Gm1 = tf(Kp, [tau, 1])
Gmz1 = c2d(Gm1, sampling_time)
num1, den1 = tfdata(Gmz1)
Bm1 = num1[0][0]
Am1 = den1[0][0]
b0m1 = Bm1[0]
a1m1 = Am1[1]

delay = ceil(theta/sampling_time)

# Close Loop Tau Calculation
tau_mf1 = ajuste1*tau
alpha1 = exp(-sampling_time/tau_mf1)

repeat = True
while repeat: 
    # inicializar  o timer
    start_time = time.time()
    kk = 1 + delay

    sendToArduino(arduinoData, '0,0')

    while kk < samples_number:
        current_time = time.time()
        if current_time - start_time > sampling_time:
            start_time = current_time
            # -----  Angle Sensor Output
            temperature_sensor[kk] = readFromArduino(arduinoData)

            # ---- Motor Model Output
            heater_model[kk] = -Am1[1] * heater_model[kk-1] + Bm1[0]*control_signal[kk-1]
            
            # Determine uncertainty
            d0barra1[kk] = temperature_sensor[kk] - heater_model[kk]

            # Determine Error
            erro1[kk] =    temperature_ref[kk] - d0barra1[kk]

            # Control Signal
            control_signal[kk] = alpha1*control_signal[kk-1] + ((1-alpha1)/b0m1)*erro1[kk] + a1m1*((1-alpha1)/b0m1)*erro1[kk-1]


            # Control Signal Saturation
            control_signal[kk] = max(min_pot, min(control_signal[kk], max_pot))

            # Motor Power String Formatation
            motors_power_packet[kk] = f"{control_signal[kk]}\r"


            sendToArduino(arduinoData, motors_power_packet[kk])
            
            
            kk += 1


    sendToArduino(arduinoData, '0,0')
    
    ### Plotar os Resultados 

    time_interval = arange(0,samples_number*sampling_time,sampling_time)

    plt.figure(1)
    plt.plot(time_interval, temperature_sensor,label='Resposta do sistema')
    plt.plot(time_interval, temperature_ref,linestyle='--',label='Referência')
    plt.legend()
    plt.xlabel('Tempo (s)')
    plt.ylabel('Temperatura (º)')
    plt.title('Resposta do Sistema')
    # plt.ylim([0,90])



    # Create a figure with two subplots
    fig, axes = plt.subplots(nrows=1, ncols=1)

    # Plot data on the first subplot (left)
    axes[0].plot(time_interval, control_signal, label='PWM')
    axes[0].set_title('Sinal de Controle')
    axes[0].set_ylabel('PWM (%)')
    axes[0].set_xlabel('Tempo (s)')
    # axes[0].set_ylim([6,16])

    
    # Add legends to each subplot
    axes[0].legend()
    # axes[1].legend()

    # Adjust layout
    plt.tight_layout()

    plt.show()

    repeat_input = input('Repeat? ')

    if repeat_input == 'n':
        repeat = False


disconnectSerial(arduinoData)