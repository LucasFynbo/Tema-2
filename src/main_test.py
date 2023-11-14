from machine import Pin, PWM
from time import sleep
import uasyncio as asyncio
import sys, select, socket, struct
import ujson as json 
import ConnectHandler

class DrvHandler:
    def __init__(self) -> None:
        self.pwm1 = PWM(Pin(14, Pin.OUT), freq=200, duty_ns= 0) # Left Moter
        self.pwm2 = PWM(Pin(15, Pin.OUT), freq=200, duty_ns= 0) # Right Motor
        self.dir_M1 = Pin(16, Pin.OUT)  # Backwards
        self.dir_M2 = Pin(13, Pin.OUT)  # Forwards

        self.mspeed: int = 131070
        self.drv: bool = 0

    def control_drv(self, duty_lm: int = 0, duty_rm: int = 0, direction: bool = -1):
        # Forwards
        if direction == 0 and duty_lm <= self.mspeed and duty_rm <= self.mspeed:
            self.dir_M1.value(self.drv)     # 0 (False) / Backwards
            self.dir_M2.value(not self.drv) # 1 (True) / Forwards
            
            self.pwm1.duty_u16(duty_lm)
            self.pwm2.duty_u16(duty_rm)
            
        # Backwards
        elif direction and duty_lm <= self.mspeed and duty_rm <= self.mspeed:
            self.dir_M1.value(not self.drv) # 1 (True) / Backwards
            self.dir_M2.value(self.drv)     # 0 (False) / Forwards
           
            self.pwm1.duty_u16(duty_lm)
            self.pwm2.duty_u16(duty_rm)
           
        else:
            sys.stdout.write('[!] Invalid parameters, motors are turned off.')
            self.pwm1.duty_u16(0)
            self.pwm2.duty_u16(0)

    def emergbrake(self) -> None:
        sys.stdout.write('[!] Emergency Brake')
        self.pwm1.duty_ns(0)
        self.pwm2.duty_ns(0)

class InHandler:
    def __init__(self) -> None:
        host: str = ConnectHandler.getip('fedora', '12345678')
        port: int = 7913
        self.ssocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        try:
            self.ssocket.bind((host,port))
            sys.stdout.write('Listeng on %s:%d' % (host, port))
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                sys.stdout.write('[i] Address is already in use. Waiting for it to be released...')
                
                # Enabler vores socket til at bruge den samme adresse, så den "ignorerer" vores EADDRINUSE error.
                self.ssocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.ssocket.bind((host, port))  # Prøver at binde igen på den genbrugte adresse.
                sys.stdout.write('[i] Listeng on %s:%d' % (host, port))
            else:
                # Andre socket errors som ikke har noget med 'already in use' at gøre. 
                sys.stdout.write('[!] Socket Error: %s' % (e))

        self.control_handler = DrvHandler()
        self.remaining_data = b''

    async def remote_control_server(self) -> None:
        while True:
            #modtager data fra klienten (fjernbetjeningen) dekoder det fra bytes til streng
            creqctrl = self.ssocket.recv(1024)
            
            print(creqctrl)
            
            unpacked = json.loads(creqctrl.decode('utf-8'))
            
            direction: bool = unpacked.get('check.direction')
            lm_val: int = unpacked.get('lm')
            rm_val: int = unpacked.get('rm')
            
            print(f"Direction: {direction}, LM: {lm_val}, RM: {rm_val}")
            
            self.control_handler.control_drv(lm_val, rm_val, direction)
            
            self.remaining_data = creqctrl
            sleep(0.05)
            
    def close_socket(self):
        self.ssocket.close()
        
async def main():
    input_handler = InHandler()
    try:
        await asyncio.gather(   
            input_handler.remote_control_server(),
        )
    finally:
        input_handler.close_socket()

if __name__ == "__main__":
    asyncio.run(main())
    