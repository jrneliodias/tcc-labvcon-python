import serial
from serial.tools.list_ports import comports


class serialApp():
    def __init__(self):
        self.serialPort = serial.Serial()
        self.baudrate = ['9600', '115200', '250000']
        self.portlist = []
        self.serialPort.timeout = 1

    # Método de Update para listar as portas seriais
    def updatePort(self):
        self.portlist = [port.device for port in comports()]
        print(self.portlist)

    # conexão
    def connectSerial(self):
        try:
            self.serialPort.open()
        except:
            print("Houve um erro ao abrir a serial.")

    # Receber Dados
    def readSerial(self):

        dataRead = self.serialPort.read(10).decode('utf-8')
        print(dataRead)

    # Enviar Dados
    def sendSerial(self, data):
        if (self.serialPort.isOpen):
            dataSend = str(self.data) + '\n'
            self.serialPort.write(dataSend.encode())
            self.serialPort.flushOutput()

    # Fechar a conexão
    def closeSerial(self):
        self.serialPort.close()

    def run(self):
        # Especifica a quantidade de bytes a serem lidos
        dataReceived = self.serialPort.read(10).decode()
        print(dataReceived)
        return dataReceived
