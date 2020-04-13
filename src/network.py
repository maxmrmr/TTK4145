import json  #parse = loads(), serialize = dumps()
import socket
from time import sleep
import threading

SENDER_IP = socket.gethostname()
BROADCAST_PORT = 1440
PRIVATE_PORT = 1560

def send(type, data, ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = {
        "type": type,
        "sender_ip": SENDER_IP,
        "data": data
    }
    message_string = json.dumps(message)
    s.sendto(message_string.encode(), (ip, PRIVATE_PORT))
    s.close()

def broadcast(type, data):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    message = {
        "type": type,
        "sender_ip": SENDER_IP,
        "data": data
    }
    message_string = json.dumps(message)
    s.sendto(message_string.encode(), ("255.255.255.255", BROADCAST_PORT))
    s.close()

def receive(sock):
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    return data

def network_test():
    while True:
        send('cost_request', {'ip': '189.10.1', 'floor': '1', 'button': '1'}, '127.0.0.1')
        sleep(3)
        broadcast('order', {'ip': '029.393', 'floor': '2', 'button': '2'})
        sleep(3)

# Running the network listener
def network_main():
    receive_private_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_private_socket.bind(("", PRIVATE_PORT))

    receive_broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_broadcast_socket.bind(("", BROADCAST_PORT))

    while True:
        data = receive(receive_private_socket)
        print("received private:", data)

        data = receive(receive_broadcast_socket)
        print("received broadvast:", data)

        sleep(0.5)

if __name__ == "__main__":
    main_thread = threading.Thread(target=network_main)
    test_thread = threading.Thread(target=network_test)
    main_thread.start()
    test_thread.start()
    main_thread.join()
    test_thread.join()
