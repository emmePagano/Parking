from machine import Pin, PWM
import time
from time import sleep

pwm = PWM(Pin(21), freq=50)
pwm.duty(26)

def set_angle(angle):
    duty_min = 26
    duty_max = 128
    pwm.duty(int(duty_min + (angle/180)*(duty_max-duty_min)))
    