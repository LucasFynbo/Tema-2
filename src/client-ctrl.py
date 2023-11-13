import tkinter as tk
import msgpack, socket
import math

class JoystickApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Joystick")

        self.canvas = tk.Canvas(self.master, width=400, height=400, bg="black")
        self.canvas.pack()
        
        self.cirkel = self.canvas.create_oval(350, 350, 50, 50, fill="white")

        self.joystick = self.canvas.create_oval(190, 190, 210, 210, fill="red")

        self.canvas.create_text(100, 300, text="Venstre, Ned", font=("Helvetica", 12))
        self.canvas.create_text(100, 100, text="Venstre, Op", font=("Helvetica", 12))
        self.canvas.create_text(300, 300, text="Højre, Ned", font=("Helvetica", 12))
        self.canvas.create_text(300, 100, text="Højre, Op", font=("Helvetica", 12))
        self.canvas.create_text(200, 50, text="Op", font=("Helvetica", 12))
        self.canvas.create_text(350, 200, text="Højre", font=("Helvetica", 12))
        self.canvas.create_text(200, 350, text="Ned", font=("Helvetica", 12))
        self.canvas.create_text(50, 200, text="Venstre", font=("Helvetica", 12))

        self.canvas.bind("<B1-Motion>", self.move_joystick)
        self.canvas.bind("<ButtonRelease-1>", self.tilbage_til_start)

        self.coords()

    def move_joystick(self, event):

        cirkel_midtpunkt = [(350 + 50) / 2, (350 + 50) / 2]
        joystick_midtpunkt = [(190 + 210) / 2, (190 + 210) / 2]
        distance = math.sqrt((event.x - cirkel_midtpunkt[0]) ** 2 + (event.y - cirkel_midtpunkt[1]) ** 2)

        if distance <= (350 - 50) / 2:
            x = event.x
            y = event.y
            x = max(10, min(390, x))
            y = max(10, min(390, y))
            self.canvas.coords(self.joystick, x - 10, y - 10, x + 10, y + 10)

    def tilbage_til_start(self, event):
        self.canvas.coords(self.joystick, 190, 190, 210, 210)

    def coords(self):
        # bmsg = str.encode(self.canvas.coords(self.joystick))
        print(self.canvas.coords(self.joystick))
        self.master.after(50, self.coords)

        return self.canvas.coords(self.joystick)

    def calcfunc(self):
        """
        Reference -
            Speed -
                UP: 200, 50
                DOWN: 200, 350

            Turn -
                Left: 50, 200
                Right: 350, 200

                Top-left: 100, 100
                Top-right: 300, 100
                Bottom-left: 100, 300
                Bottom-right: 300, 300
        """
        coords = self.canvas.coords(self.joystick)

        # Calculate speed (how far user is up/down)
        speed_factor = 327
        speed = (self.canvas.coords(self.joystick)[1]-50)/1 # hvis 1 er = 1grad
        speed = max(0, speed) # der kan ikke køres i negativ (kan nok ikke køre baglæns)
        speed_value = int(speed * speed_factor)
        
        uspeed: int = 0
        for counter in range(coords[0]):
            uspeed += 327
            counter += 1    # Maybe not needed
            
        # Calculate turn (how far user is in/out)
        

class UDPSocket:
    def __init__(self):
        saddr = '0.0.0.0'
        sport = '0'
        csocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        ssocket_addr = (saddr, sport) 
        buffer_size: int = 1024

        data = {
            'coordinates': math.floor(JoystickApp.coords())
            
        }


if __name__ == "__main__":
    root = tk.Tk()
    app = JoystickApp(root)
    root.mainloop()