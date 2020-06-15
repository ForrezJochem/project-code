import spidev
from time import sleep
import RPi.GPIO as GPIO


class ADC:
    def __init__(self, max_speed):
        self.max_speed = max_speed
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = self.max_speed

    def analogRead(self, channel):
        adc = self.spi.xfer2([1, (8+channel) << 4, 0])
        data = ((adc[1] & 3) << 8) + adc[2]
        return data