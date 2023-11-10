from machine import Pin, PWM
from time import sleep
import numpy as np #styring af bit. (Resource Management)
import msgpack as mp #binær overførelse af data i stedet for json.


pwm1 = PWM(Pin(14, Pin.OUT), freq=200, duty_ns= 0)
pwm2 = PWM(Pin(15, Pin.OUT), freq=200, duty_ns= 0)
dir_M1 = Pin(16, Pin.OUT)
dir_M2 = Pin(13, Pin.OUT)

# ------------------------------
#       UDP socket server
# ------------------------------
#           Insert

def main():

    # Control loop

    direction = "0"
    # direction = w; kør fremad  
    # direction = a; kør venstre
    # direction = d; kør højre
    # direction = s; kør bagud
    match (direction):
        case w:
            # kør fremad
            return
        case a:
            #kør venstre
            return
        case d:
            #kør højre
            return
        case s:
            #bak/brems
            return
        
        
if __name__ == "__main__":
    main()

