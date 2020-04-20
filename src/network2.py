"""Network protocoll to use tcp to make up for packet loss in elevator alg
"""
import threading
import socket
import threading
from time import sleep
import pprint
import json
import traceback

class Network_manager():

    broadcast_port = 1440 # kanskje dumt å bare iterere en slik opp
    tcp_timeout_val = 3.0
 
    def __init__(self, callback, id, verbose = False):
        self.connections = {}
        self.id = id
        self.callback = callback
        self.connections_lock = threading.Lock()
        self.verbose = verbose

        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server.bind(('', 0)) # This binds the socket to a port given by the operating system
        self.tcp_server.listen(1)


        self.tcp_server_port = self.tcp_server.getsockname()[1]


    def _broadcast_adress(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        id_dict = {'elev_id': self.id, 'tcp_port': self.tcp_server_port}
        id_str = json.dumps(id_dict)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        while True:
            s.sendto(id_str.encode(), ("255.255.255.255", Network_manager.broadcast_port))
            sleep(1.0)

    def _listen_for_adress(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", Network_manager.broadcast_port))

        while True:
            data, addr = s.recvfrom(1024)
            data = json.loads(data.decode('utf-8'))
            self._hande_incomming_adress(data, addr)

    def _add_connection(self, remote_ID, s):
        self.connections[remote_ID] = {'elev_id': remote_ID, 'socket': s, 'listener': self._make_thread_for_tcp_listener(s)}

    def _hande_incomming_adress(self, data, addres):
        """ Get the incomming adress, try to obtain a tcp connection with it and add the socket to self.connections
        """
        #print(f'manager {self.id} received data: {data} addres: {addres}')
        
        self.connections_lock.acquire()
        remote_ID = data['elev_id']
        try:
            if not remote_ID in self.connections and not remote_ID == self.id: # Only active connections shall be in the dictionary
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #s.settimeout(Network_manager.tcp_timeout_val)
                s.connect((addres[0], data['tcp_port']))
                id_dict = {'elev_id': self.id}
                id_str = json.dumps(id_dict)
                s.send(id_str.encode()) # Send own ID as first package when connecting to other managers server
                self._add_connection(remote_ID, s) #adds the connection to the dictionary of connections
                if self.verbose == True:
                    print(f'manager {self.id} -> server {remote_ID}')
        except:
            traceback.print_exc()
        finally:
            self.connections_lock.release()

    def _make_thread_for_tcp_listener(self, s):
        """Return thread for listening for incomming tcp packets
        """
        t = threading.Thread(target = self._handle_incomming_tcp_data, args=(s,))
        t.start()
        return t

    def _tcp_recv(self, s):
        #s.settimeout(Network_manager.tcp_timeout_val)
        #s.setblocking(1)
        data = s.recv(1024)
        return json.loads(data.decode('utf-8'))

    def _hande_inncomming_connections(self):
        
        while True:
            s, _ = self.tcp_server.accept()
            self.connections_lock.acquire() # lock for adding connections to own conections

            try:
                data = self._tcp_recv(s)
                remote_ID = data['elev_id']
                if not remote_ID in self.connections:
                     self._add_connection(remote_ID, s)
                     if self.verbose == True:
                        print(f'manager {self.id} <- client: {remote_ID}')
            except:
                traceback.print_exc()
            finally:
                self.connections_lock.release()

    def _handle_incomming_tcp_data(self, s):
        
        while True: # Problem is that this tries to read from the datastream contionously
            try:
                data = self._tcp_recv(s)
                self.callback(data)
            except:
                traceback.print_exc()
            finally:
                pass


    def run(self):
        
        broadcast_thread = threading.Thread(target=self._broadcast_adress)
        listen_thread = threading.Thread(target = self._listen_for_adress)
        server_thread = threading.Thread(target = self._hande_inncomming_connections)

        broadcast_thread.start()
        server_thread.start()
        listen_thread.start()


    def send(self, message):
        msg_str = json.dumps(message)
        msg_encoded = msg_str.encode()

        for key, value in self.connections.items():

            try: # Shoud make som e logic to handle situations where the connectin has failed
                value['socket'].send(msg_encoded)
            except:
                pass
            finally:
                pass
            
       


if __name__ == "__main__":
    amount = 5
    managers = [Network_manager(lambda x: pprint.pprint(x) , id) for id in range(amount)]
    [m.run() for m in managers]

    sleep(5.0)
    #pprint.pprint([(m.id, m.connections) for m in managers])
    managers[0].send({'some_msg': 'some important msg'})

    
