from machine import Pin, PWM
from time import sleep
import uasyncio as asyncio
import sys, select

# ------------------------------
# UDP socket server
# ------------------------------
# Insert

class DrvHandler:
    def __init__(self) -> None:
        self.pwm1 = PWM(Pin(14, Pin.OUT), freq=200, duty_ns= 0) # Left Moter
        self.pwm2 = PWM(Pin(15, Pin.OUT), freq=200, duty_ns= 0) # Right Motor
        self.dir_M1 = Pin(16, Pin.OUT)  # Backwards
        self.dir_M2 = Pin(13, Pin.OUT)  # Forwards


=======
        self.mspeed: int = 65535
        self.drv: bool = 0


    def turner(self, direction: int = 2) -> None:
        # 0 - Left, 1 - Right, (DEFAULT) 2 - Placeholder
        if direction <= 0:
            self.pwm1.duty_u16(0)
            self.pwm2.duty_u16(self.mspeed)
        elif 0 < direction < 2:
            self.pwm2.duty_u16(0)
            self.pwm1.duty_u16(self.mspeed)
            



=======
    def frwd(self) -> None:
        self.pwm1.duty_u16(self.mspeed)
        self.pwm2.duty_u16(self.mspeed)

        self.dir_M1.value(self.drv)     # 0 (False) / Backwards
        self.dir_M2.value(not self.drv) # 1 (True) / Forwards
        
    def bckwd(self) -> None:
        self.pwm1.duty_u16(self.mspeed) 
        self.pwm2.duty_u16(self.mspeed) 

        self.dir_M1.value(not self.drv) # 1 (True) / Backwards
        self.dir_M2.value(self.drv)     # 0 (False) / Forwards

    def emergbrake(self) -> None:
        sys.stdout.write('[!] Emergency Brake')
        self.pwm1.duty_ns(0)
        self.pwm2.duty_ns(0)

class InHandler:
    def __init__(self) -> None:
        self.key: str = ''

    async def getctrl(self, control_handler: DrvHandler) -> None:
        poller = select.poll()
        poller.register(sys.stdin, select.POLLIN)

        while True:
            events = poller.poll(10)
            for fd, event in events:
                if event & select.POLLIN:
                    self.key: str = sys.stdin.readline(1)
                    sys.stdout.write('%s' % (self.key))
                    if self.key == 'w':
                        control_handler.frwd()
                    elif self.key == 's':
                        control_handler.bckwd()
                    elif self.key == 'a':
                        control_handler.turner(0)
                    elif self.key == 'd':
                        control_handler.turner(1) 
                    elif self.key == 'q':
                        control_handler.emergbrake()
                        
            await asyncio.sleep_ms(10)

async def main():
    control_handler = DrvHandler()
    input_handler = InHandler()
    await asyncio.gather(   
        input_handler.getctrl(control_handler),
    )

if __name__ == "__main__":
    asyncio.run(main())

