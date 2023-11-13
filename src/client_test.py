import tkinter as tk
import msgpack, socket
import math

data = {}
x_value = 0
y_value = 0

class Joystick:
    def __init__(self, master):
        self.master = master
        self.master.title("Joystick")

        self.canvas = tk.Canvas(self.master, width=400, height=400, bg="white")
        self.canvas.pack()

        self.radius = 150
        self.center_x = 200
        self.center_y = 200

        # Draw the bounding box (circle)
        self.canvas.create_oval(
            self.center_x - self.radius,
            self.center_y - self.radius,
            self.center_x + self.radius,
            self.center_y + self.radius,
            outline="black"
        )

        # Draw lines from center to each corner (you can remove these as needed)
        self.canvas.create_line(self.center_x, self.center_y, self.center_x - self.radius, self.center_y - self.radius, fill="black")
        self.canvas.create_line(self.center_x, self.center_y, self.center_x + self.radius, self.center_y - self.radius, fill="black")
        self.canvas.create_line(self.center_x, self.center_y, self.center_x - self.radius, self.center_y + self.radius, fill="black")
        self.canvas.create_line(self.center_x, self.center_y, self.center_x + self.radius, self.center_y + self.radius, fill="black")

        # Draw the coordinate system inside the circle
        self.canvas.create_line(self.center_x, self.center_y - self.radius, self.center_x, self.center_y + self.radius, fill="black")  # Vertical line (Y-axis)
        self.canvas.create_line(self.center_x - self.radius, self.center_y, self.center_x + self.radius, self.center_y, fill="black")  # Horizontal line (X-axis)

        # Draw markers for reference (you can remove these as needed)
        # Middle marker
        self.draw_marker(self.center_x, self.center_y, "Middle")

        # Corner markers
        self.draw_marker(self.center_x - self.radius, self.center_y - self.radius, "Top Left")
        self.draw_marker(self.center_x + self.radius, self.center_y - self.radius, "Top Right")
        self.draw_marker(self.center_x - self.radius, self.center_y + self.radius, "Bottom Left")
        self.draw_marker(self.center_x + self.radius, self.center_y + self.radius, "Bottom Right")

        # Side markers
        self.draw_marker(self.center_x, self.center_y - self.radius, "Top")
        self.draw_marker(self.center_x, self.center_y + self.radius, "Bottom")
        self.draw_marker(self.center_x - self.radius, self.center_y, "Left")
        self.draw_marker(self.center_x + self.radius, self.center_y, "Right")

        # Draw the marker
        self.marker_size = 10
        self.marker = self.canvas.create_oval(
            self.center_x - self.marker_size // 2,
            self.center_y - self.marker_size // 2,
            self.center_x + self.marker_size // 2,
            self.center_y + self.marker_size // 2,
            fill="red"
        )

        # Bind mouse events
        self.canvas.bind("<B1-Motion>", self.move_marker)

    def draw_marker(self, x, y, label):
        # Draw a marker at the specified position with a label
        marker_size = 5
        self.canvas.create_oval(
            x - marker_size,
            y - marker_size,
            x + marker_size,
            y + marker_size,
            fill="blue"
        )
        self.canvas.create_text(x, y - marker_size - 10, text=label, fill="blue")

    def move_marker(self, event):
        global x_value, y_value
        # Calculate the new position based on mouse coordinates
        new_x = event.x
        new_y = event.y

        # Calculate the angle and distance even when clicked outside the circle
        angle = math.atan2(new_y - self.center_y, new_x - self.center_x)
        distance = min(self.radius, math.sqrt((new_x - self.center_x)**2 + (new_y - self.center_y)**2))

        # Calculate new coordinates
        new_x = self.center_x + distance * math.cos(angle)
        new_y = self.center_y + distance * math.sin(angle)

        # Update the marker position
        self.canvas.coords(
            self.marker,
            new_x - self.marker_size // 2,
            new_y - self.marker_size // 2,
            new_x + self.marker_size // 2,
            new_y + self.marker_size // 2
        )

        # Print the polar coordinates
        polar_radius = math.sqrt((new_x - self.center_x)**2 + (new_y - self.center_y)**2)
        polar_angle = math.degrees(math.atan2(new_y - self.center_y, new_x - self.center_x))
        print(f"Marker position: ({polar_radius:.2f}, {polar_angle:.2f} degrees)")
        x_value = math.floor(polar_radius)
        y_value = math.floor(polar_angle)
        calc = Calc()
        calc.calculate()

class Calc:
    def __init__(self):
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

        self.X: int = x_value
        self.Y: int = y_value

    def calculate(self):
        speed_factor: int = 436      # (436 = 65535 (mspeed) / 150 (max x value))      
        self.uspeed: int = 0
        for counter in range(self.X):
            self.uspeed += speed_factor
            counter += 1    # Maybe not needed

        # 0 for forwards, 1 for backwards
        self.checkdir = -1
        self.lm_speed = self.uspeed
        self.rm_speed = self.uspeed
        # Forwards (if Y is negative)
        if self.Y <= 0:
            self.checkdir = 0
            # top left square
            if self.Y < -90:
                print("Top Left")
                self.lm_speed = max(0, int(self.uspeed * (1 - abs(self.Y + 90) / 90)))
                print(f"left motor: {self.lm_speed}, right motor: {self.rm_speed}")
            # top right square
            elif self.Y > -90:
                print("Top Right")
                self.rm_speed = max(0, int(self.uspeed * (1 - abs(self.Y + 90) / 90)))
                print(f"left motor: {self.lm_speed}, right motor: {self.rm_speed}")
            else:
                print(f"left motor: {self.lm_speed}, right motor: {self.rm_speed}")
        
        # Backwards (if Y is positive)
        elif self.Y > 0:
            self.checkdir = 1
            # bottom left square
            if self.Y > 90:
                print("Bottom Left")
                self.rm_speed = max(0, int(self.uspeed * (1 - abs(self.Y - 90) / 90)))
                print(f"left motor: {self.lm_speed}, right motor: {self.rm_speed}")
            # bottom right square
            elif self.Y < 90: 
                print("Bottom Right")
                self.lm_speed = max(0, int(self.uspeed * (1 - abs(self.Y - 90) / 90)))
                print(f"left motor: {self.lm_speed}, right motor: {self.rm_speed}")
            else: 
                print(f"left motor: {self.lm_speed}, right motor: {self.rm_speed}")
        
        self.craft_data

    def craft_data(self):
        global data
         # craft data from calculations.
        data = {
            'check.direction': self.checkdir,
            'lm': self.lm_speed,
            'rm': self.rm_speed,
        }

class USocket:
    def __init__(self):
        #Intialize the UDP socket
        self.csocket = socket.socket(family=socket.AF.INET, type=socket.SOCK_DGRAM)

        self.saddr = '000.0.0.0' #indsæt IP adresse her!
        self.sport = 7913 #indsæt hvilken port der bliver brugt!
        self.ssocket_addr = (self.saddr, self.sport) #henter oplysningerne fra self.addr(ip) og self.sport(port)
        self.buffer_size: int = 1024

    def send_data(self):
        global data
        #forbereder data der skal sendes over UDP
        packed_data = msgpack.packb(data)#pak dataen ved hjælp af msgpack for effektiv konventering til sekvens format
        self.csocket.sendto(packed_data, self.ssocket_addr)#sender pakken af data via UDP

if __name__ == "__main__":
    root = tk.Tk()
    app = Joystick(root)

    def update_udp():
        USocket.send_data(None)#periode vis sender kordinater fra joystik over UDP
        root.after(50, update_udp)#planlægger næste opdatering af data til 50 millisekunder
    
    root.after(50, update_udp) #starter opdateringen
    root.mainloop() #starter Tkinter main loop"