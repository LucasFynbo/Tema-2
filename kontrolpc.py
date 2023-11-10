import seocket
import keyboard

def send_com(command, host="roverens_ip", port = 7913):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    