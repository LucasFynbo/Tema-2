from machine import Pin, PWM
import time
 
pwm1 = PWM(Pin(14, Pin.OUT), freq=200, duty_ns= 0)
pwm2 = PWM(Pin(15, Pin.OUT), freq=200, duty_ns= 0)
dir_M1 = Pin(16, Pin.OUT)
dir_M2 = Pin(13, Pin.OUT)
 
frem = 0
speed = 65535
 
try:
    while True:
        pwm1.duty_u16(speed)
        pwm2.duty_u16(speed)
        dir_M1.value(not frem)
        dir_M2.value(frem)
        time.sleep(0.1)
 
except KeyboardInterrupt:
    print("Program afbrudt. Stopper motoren.")
    pwm1.duty_ns(0)
    pwm2.duty_ns(0)