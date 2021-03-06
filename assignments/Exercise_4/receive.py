import socket
from time import sleep
BROADCAST_PORT = 1440
PRIVATE_PORT = 1560

PORT_IN_USE = PRIVATE_PORT

def receive():
    data, addr = receive_socket.recvfrom(1024) # buffer size is 1024 bytes
    return data


receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receive_socket.bind(("", PORT_IN_USE))

while (True):
    data = receive()
    print("received message:", data)
    sleep(0.5)
