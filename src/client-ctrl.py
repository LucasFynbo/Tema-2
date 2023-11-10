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