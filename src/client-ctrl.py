import tkinter as tk
import socket
import math
import json
 

# Initialser globale variabler.
data = {}   # Vores data vi sender i vores UDP Packet.
x_value = 0 # Marker position på x aksen.
y_value = 0 # Marker position på y aksen.

# Joystick GUI app, main class
class Joystick:
    def __init__(self, master):
        self.master = master    # Når der er flere vinduer i en applikation skaber det et hieraki af vinduer (ligesom et folder tree (parent/child))
                                # Her siger vi at vores joystick app skal startes som root vinduet, da det er det primære vindue.

        self.master.title("Joystick")   # Sætter en header for vores app, kan ikke ses på mobil.

        self.canvas = tk.Canvas(self.master, width=1080, height=2400, bg="white") # Bygger selve applikations vinduet
        self.canvas.pack() # Packer selve vores GUI i vores root vindue. Uden denne vil vores root vindue være tomt og vi vil ikke kunne se vores GUI.

        # Cirkel size parameters.
        self.radius = 450
        self.center_x = 550
        self.center_y = 1050

        # Tegner vores boundary cirkel der sætter en limit for hvor langt vores marker kan køres ud.
        # Da vores cirkel coords bruger x og y koordinater, tilføjer vi vores radius til hvert aksel (x+, x-, y+, y-)
        self.canvas.create_oval(
            self.center_x - self.radius,
            self.center_y - self.radius,
            self.center_x + self.radius,
            self.center_y + self.radius,
            outline="black"
        )

        # Tegner vores kordinat lignende linjer i cirkelen.
        self.canvas.create_line(self.center_x, self.center_y - self.radius, self.center_x, self.center_y + self.radius, fill="black")  # Vertical line (Y-axis)
        self.canvas.create_line(self.center_x - self.radius, self.center_y, self.center_x + self.radius, self.center_y, fill="black")  # Horizontal line (X-axis)

        # Tegner vores control marker
        self.marker_size = 30
        # Følgende parameter gør vores marker til en cirkel.
        self.marker = self.canvas.create_oval(
            self.center_x - self.marker_size // 2,
            self.center_y - self.marker_size // 2,
            self.center_x + self.marker_size // 2,
            self.center_y + self.marker_size // 2,
            fill="red"
        )

        # Kalder self.move_marker funktionen når vores marker er i bevægelse.
        self.canvas.bind("<B1-Motion>", self.move_marker)
        # Kalder vores self.release funktion når vores marker er sluppet.
        self.canvas.bind("<ButtonRelease-1>", self.release)

    # Marker release funktion.
    def release(self, event):
        # Tager vores current x og y kordinator og sætter dem til x center og y center.
        global x_value, y_value
        rel_x = event.x
        rel_y = event.y

        rel_x = self.center_x 
        rel_y = self.center_y

        # Tegner vores marker igen, da den ikke opdaterer til center uden redrawing.
        self.canvas.coords(
            self.marker,
            rel_x - self.marker_size // 2,
            rel_y - self.marker_size // 2,
            rel_x + self.marker_size // 2,
            rel_y + self.marker_size // 2
        )

        # Kopieret fra vores move_marker funktion, bedre kode skik at ligge det i en funktion for sig selv istedet.
        # Kan implementeres senere.

        # Udregner vores marker position i vores koordinat system.
        self.polar_radius = math.sqrt((rel_x - self.center_x)**2 + (rel_y - self.center_y)**2)
        self.polar_angle = math.degrees(math.atan2(rel_y - self.center_y, rel_x - self.center_x))
        print(f"Marker position: ({self.polar_radius:.2f}, {self.polar_angle:.2f} degrees)")

        # Runder vores float ned til en int.
        x_value = math.floor(self.polar_radius)
        y_value = math.floor(self.polar_angle)

        # Kalder vores calculate funktion, sådan vi opdaterer vores UDP packet data med den nye marker position.
        calc = Calc()
        calc.calculate()

    # Vores move_marker funktion. Virker meget ligesom vores release funktion, bare den ikke returnerer tilbage til x center og y center.
    def move_marker(self, event):
        # Henter vores current marker position fra vores globale variabler.
        global x_value, y_value
        new_x = event.x
        new_y = event.y

        # Calculate the angle and distance even when clicked outside the circle
        angle = math.atan2(new_y - self.center_y, new_x - self.center_x)
        distance = min(self.radius, math.sqrt((new_x - self.center_x)**2 + (new_y - self.center_y)**2))

        # Calculater vores marker's position indenfor vores koordinat system.
        new_x = self.center_x + distance * math.cos(angle)  # X akse
        new_y = self.center_y + distance * math.sin(angle)  # Y akse

        # Redrawer vores marker igen for at opdatere visuelt den nye position.
        self.canvas.coords(
            self.marker,
            new_x - self.marker_size // 2,
            new_y - self.marker_size // 2,
            new_x + self.marker_size // 2,
            new_y + self.marker_size // 2
        )

        # Udregner vores marker position i vores koordinat system.
        self.polar_radius = math.sqrt((new_x - self.center_x)**2 + (new_y - self.center_y)**2)
        self.polar_angle = math.degrees(math.atan2(new_y - self.center_y, new_x - self.center_x))
        print(f"Marker position: ({self.polar_radius:.2f}, {self.polar_angle:.2f} degrees)")
        x_value = math.floor(self.polar_radius)
        y_value = math.floor(self.polar_angle)

        # Opdaterer vores UDP packet med det nye marker position data.
        calc = Calc()
        calc.calculate()

class Calc:
    def __init__(self):
        # Initialiser vores variabler
        self.X: int = x_value
        self.Y: int = y_value

    def calculate(self):
        speed_factor: int = 145 # (145 = 65535 (mspeed) / 450 (self.radius))      
        self.uspeed: int = 0

        # Pluser vores speed factor til vores self.uspeed variabel for hvor langt vores marker er ude på x aksen.
        for i in range(self.X):
            self.uspeed += speed_factor

        self.checkdir = -1 # 0 for forwards, 1 for backwards. -1 = default value.

        # Defaulter left motor (lm) og right motor (rm) speed variables til self.uspeed.
        self.lm_speed = self.uspeed
        self.rm_speed = self.uspeed
        
        # Main control loop for UDP packet data crafting.
        if self.Y <= 0: # Forwards (if Y is negative)
            self.checkdir = 0   # Forwards (marker in top half of circle)
            
            if self.Y < -90: # Top Left
                print("Top Left")
                self.lm_speed = max(0, int(self.uspeed * (1 - abs(self.Y + 90) / 90)))
                print(f"left motor: {self.lm_speed}, right motor: {self.rm_speed}")
            
            elif self.Y > -90: # Top Right
                print("Top Right")
                self.rm_speed = max(0, int(self.uspeed * (1 - abs(self.Y + 90) / 90)))
                print(f"left motor: {self.lm_speed}, right motor: {self.rm_speed}")
            else:
                print(f"left motor: {self.lm_speed}, right motor: {self.rm_speed}")
        
        elif self.Y > 0: # Backwards (if Y is positive)
            self.checkdir = 1   # Backwards (marker in bottom half of circle)
            
            if self.Y > 90: # Bottom Left
                print("Bottom Left")
                self.lm_speed = max(0, int(self.uspeed * (1 - abs(self.Y - 90) / 90)))
                print(f"left motor: {self.lm_speed}, right motor: {self.rm_speed}")
            
            elif self.Y < 90: # Bottom Right
                print("Bottom Right")
                self.rm_speed = max(0, int(self.uspeed * (1 - abs(self.Y - 90) / 90)))
                print(f"left motor: {self.lm_speed}, right motor: {self.rm_speed}")
            else: 
                # Else statement for security, som applikationen er bygget vil dette aldrig blive eksekveret.
                print(f"left motor: {self.lm_speed}, right motor: {self.rm_speed}")
        
        # Kalder vores UDP packet crafter funktion med vores variabler.
        self.craft_data()

    # Craft vores UDP packet vi sender til vores server.
    def craft_data(self):
        global data
         # craft data from calculations.
        data = {
            'check.direction': self.checkdir,  # direction variabel, forwards (activate M2) eller backwards (activate M1)
            'lm': self.lm_speed,    # Left motor speed
            'rm': self.rm_speed,    # Right motor speed
        }

# UDP socket class
class UdpSocket:
    def __init__(self):
        #Intialize the UDP socket
        self.csocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.saddr = '10.42.0.139' # indsæt IP adresse her!
        self.sport = 7913 # indsæt hvilken port der bliver brugt!
        self.ssocket_addr = (self.saddr, self.sport) # henter oplysningerne fra self.addr(ip) og self.sport(port)
        self.buffer_size: int = 1024

    def send_data(self):
        global data
        #forbereder data der skal sendes over UDP
        packed_data = json.dumps(data) # pak dataen ved hjælp af msgpack for effektiv konventering til sekvens format
        self.csocket.sendto(packed_data.encode('utf-8'), self.ssocket_addr) # sender pakken af data via UDP

if __name__ == "__main__":
    csocket = UdpSocket()
    root = tk.Tk()
    app = Joystick(root)

    def update_udp():
        csocket.send_data()#periode vis sender kordinater fra joystik over UDP
        root.after(50, update_udp)#planlægger næste opdatering af data til 50 millisekunder
    
    root.after(50, update_udp) #starter opdateringen
    root.mainloop() #starter Tkinter main loop