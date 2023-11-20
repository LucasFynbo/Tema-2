from machine import Pin, PWM #Bibliotekter til styring af hardware
from time import sleep # Funktioner til håndtering af tid
import uasyncio as asyncio #Asynkron I/O-bibliotek
import sys, select, socket, struct #system-, socket og strukturbiblioteker
import ujson as json # bibliotek til håndtering af JSON-data
import ConnectHandler #tilslutningshåndteringsmodul


#klasse til håndtering af motorstyring
class DrvHandler:
    def __init__(self) -> None:

#Initalisering af PWM-pinde til motorer og styringspinde for retning (ESP32 pins)        
        self.pwm1 = PWM(Pin(14, Pin.OUT), freq=200, duty_ns= 0) # Venstre Moter
        self.pwm2 = PWM(Pin(15, Pin.OUT), freq=200, duty_ns= 0) # Højre Motor
        self.dir_M1 = Pin(16, Pin.OUT)  # Baglæns
        self.dir_M2 = Pin(13, Pin.OUT)  # Fremad

#indstilling af standardmotorhastighed og retning
        self.mspeed: int = 131070
        self.drv: bool = 0 #False repræsenterer baglæns, True er fremad

#Funktion til at styre motorstyring
    def control_drv(self, duty_lm: int = 0, duty_rm: int = 0, direction: bool = -1):

#køre fremad
        if direction == 0 and duty_lm <= self.mspeed and duty_rm <= self.mspeed:
            self.dir_M1.value(self.drv)     # 0 (False) / sætter venstremotorens retning (baglæns)
            self.dir_M2.value(not self.drv) # 1 (True) / sætter højremotorens retning (fremad)
            
            self.pwm1.duty_u16(duty_lm) #sætter dutycyklus for venstremotor
            self.pwm2.duty_u16(duty_rm) #sætter dutycyklus for højremotor
            

#køre baglæns
        elif direction and duty_lm <= self.mspeed and duty_rm <= self.mspeed:
            self.dir_M1.value(not self.drv) # 1 (True) / sætter venstremotorens retning (fremad)
            self.dir_M2.value(self.drv)     # 0 (False) / Fsætter højremotorens retning (baglæns)
           
            self.pwm1.duty_u16(duty_lm) #sætter dutycyklus for venstremotor
            self.pwm2.duty_u16(duty_rm) #sætter dutycyklus for højremotor
           
        else:
            sys.stdout.write('[!] Invalid parameters, motors are turned off.')
            self.pwm1.duty_u16(0) #sluk venstremotor
            self.pwm2.duty_u16(0) #sluk højremotor


#funktion til nødbremse
    def emergbrake(self) -> None:
        sys.stdout.write('[!] Emergency Brake')
        self.pwm1.duty_ns(0) #stop venstremotor
        self.pwm2.duty_ns(0) #stop højremotor

#Klasse til håndtering af indkommend data
class InHandler:
    def __init__(self) -> None:
        host: str = ConnectHandler.getip('fedora', '12345678') #SSID og PASS
        port: int = 7913 #portnummer
        
#Opret en socket til UDP-kommunikation
        self.ssocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        
        try:
#forsøg at binde en socket til den angivne vært og port            
            self.ssocket.bind((host,port))
            sys.stdout.write('Listeng on %s:%d' % (host, port)) # vis lyttemeddelelse
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

        self.control_handler = DrvHandler() #Initialiser motorstyring
        self.remaining_data = b'' #initialiser buffer til resterende data

#Asynkron funktion til fjernbetjeningsserver
    async def remote_control_server(self) -> None:
        while True:
            #modtager data fra klienten (fjernbetjeningen) dekoder det fra bytes til streng
            creqctrl = self.ssocket.recv(1024)
            
            print(creqctrl) #udskriv modtaget kontroldata

#afkod modtaget JSON-data            
            unpacked = json.loads(creqctrl.decode('utf-8'))
            direction: bool = unpacked.get('check.direction') #hent retnings værdi
            lm_val: int = unpacked.get('lm') #hent værdi for venstre motor
            rm_val: int = unpacked.get('rm') #hent værdi for højre motor
            
            print(f"Direction: {direction}, LM: {lm_val}, RM: {rm_val}") #udskriv analyserde data

#styr motorer basert på modtagne data            
            self.control_handler.control_drv(lm_val, rm_val, direction)
            
#opdatering af variablen for resterende data og en kort pause
            self.remaining_data = creqctrl
            sleep(0.05)

#Funktion til at lukke socket-forbindelsen            
    def close_socket(self):
        self.ssocket.close()# lukker den åbne socket-forbindelse

#hovedasynkrone funktion        
async def main():
    input_handler = InHandler() #opretter en instans af InHandler-klassen
    try:
        await asyncio.gather(   
            input_handler.remote_control_server(),#starter fjernbetjningens-serveren
        )
    finally:
        input_handler.close_socket()#lukker socket-forbindelsen ved afslutning

#kører hovedasynkronfunktionaliteten, der styrer fjernbetjeningens-serveren
if __name__ == "__main__":
    asyncio.run(main())
