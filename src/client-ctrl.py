import tkinter as tk

class JoystickApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Min Fede Joystick App")

        self.canvas = tk.Canvas(self.master, width=400, height=400, bg="pink")
        self.canvas.pack()

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

        self.update_coordinates()

    def move_joystick(self, event):
        x = event.x
        y = event.y

        x = max(10, min(390, x))
        y = max(10, min(390, y))

        self.canvas.coords(self.joystick, x - 10, y - 10, x + 10, y + 10)

    def tilbage_til_start(self, event):
        self.canvas.coords(self.joystick, 190, 190, 210, 210)

    def update_coordinates(self):
        print(self.canvas.coords(self.joystick))
        self.master.after(100, self.update_coordinates)

if __name__ == "__main__":
    root = tk.Tk()
    app = JoystickApp(root)
    root.mainloop()



import seocket
import keyboard

#dette er funktionen til at sende komandoer til roveren
def send_com(command, host="roverens_ip", port = 7913):
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #opretter TCP-socket
    
    client_socket.connect((host,port)) #opretter forbindelse til serverne (roveren)

    client_socket.send(command.encode('utf-8')) #sender komandoer til roveren efter de er lavet til bytes :) 
    
    client_socket.close() # lukker forbindelsen

#loppe der køre forevig til brugeren lukker programmet.
while True:
    if keyboard.is_pressed('w'):
        send_styring('w')

    elif keyboard.is_pressed('s'):
        send_styring('s')
    elif keyboard.is_pressed('a'):
        send_styring('a')
    elif keyboard.is_pressed('d'):
        send_styring('d')
    elif keyboard.is_pressed('q'):
        send_styring('q')

