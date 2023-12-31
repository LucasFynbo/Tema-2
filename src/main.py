from machine import Pin, PWM
from time import sleep
import uasyncio as asyncio
import sys, select, socket, struct
import ujson as json 
import ConnectHandler

class DrvHandler:
    def __init__(self) -> None:
        self.pwm1 = PWM(Pin(14, Pin.OUT), freq=100, duty_ns= 0) # Left Moter
        self.pwm2 = PWM(Pin(15, Pin.OUT), freq=100, duty_ns= 0) # Right Motor
        self.dir_M1 = Pin(16, Pin.OUT)  # Backwards
        self.dir_M2 = Pin(13, Pin.OUT)  # Forwards

        self.mspeed: int = 65535
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
        host: str = ConnectHandler.getip('fedora', '12345678')#SSID PASSWD
        port: int = 7913 #hvad port der brugres
        self.ssocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #opretter UDP ved hjælp af Pythons standart bib
        
        try:
            self.ssocket.bind((host,port)) #binder socket til SSIG og port 
            sys.stdout.write('Listeng on %s:%d' % (host, port))#lytter på SSID og port
        except OSError as e:
            if e.errno == errno.EADDRINUSE: #opfanger fejl i forsøget til at forbinde socket og tildeles variablen "e"
                sys.stdout.write('[i] Address is already in use. Waiting for it to be released...')
                self.ssocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)# Enabler vores socket til at bruge den samme adresse, så den "ignorerer" vores EADDRINUSE error.
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
            creqctrl = self.ssocket.recv(1024) #kan modtage op til 1024 bytes af gangen
            
            print(creqctrl)
            
            unpacked = json.loads(creqctrl.decode('utf-8'))#laves fra bytes til steng og indlæses som json data
            
            direction: bool = unpacked.get('check.direction')#ser efter retning på motor
            lm_val: int = unpacked.get('lm')
            rm_val: int = unpacked.get('rm')
            
            print(f"Direction: {direction}, LM: {lm_val}, RM: {rm_val}")
            
            self.control_handler.control_drv(lm_val, rm_val, direction) #styre enhed baseret på modtagende data
            
            self.remaining_data = creqctrl #opdatere med modtagende data
            sleep(0.05) #tilføjer en kort pause 
            
    def close_socket(self): #lukker forbindelsen kort
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
