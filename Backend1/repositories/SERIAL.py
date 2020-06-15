from RPi import GPIO
from serial import Serial, PARITY_NONE
import time


class SERIAL:
    def __init__(self, tx=27, tx_port="/dev/ttyAMA0"):
        self.tx = tx
        self.tx_port = "/dev/ttyAMA0"

        self.__initGPIO()

    def __initGPIO(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.tx, GPIO.OUT)

    def send(self, message):
        if message != "Null":
            ser = Serial(self.tx_port)
            print(message)
            ser.write(message.encode(encoding='utf-8'))
    def send_action(self, message):
        if message != "Null":
            ser = Serial(self.tx_port)
            print(message)
            ser.write(message)

    def send_recive(self, message):
        ser = Serial(self.tx_port)
        ser.write(message.encode(encoding='utf-8'))
        return self.read()

    def read(self):
        with Serial('/dev/ttyAMA0', 9600, bytesize=8, parity=PARITY_NONE, stopbits=1) as port:
            while True:
                line = port.readline()
                return line

