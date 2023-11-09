ssid = 'your_wifi_ssid'
password = 'your_wifi_password'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

server_ip = 'your_server_ip'
server_port = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((server_ip, server_port))
