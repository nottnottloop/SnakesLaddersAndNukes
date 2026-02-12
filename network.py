import socket
import pickle
import configparser
config = configparser.ConfigParser()

class Network:
    def __init__(self):
        self.create_socket()

    def create_socket(self):
        self.client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        config.read('gameconfig.ini')
        self.server = config['Server']['ip']
        self.port = int(config['Server']['port'])
        # self.server = "192.168.1.79"
        # self.port = 5555
        self.addr = (self.server, self.port)
        self.p = -1

    def get_p(self):
        self.create_socket()
        self.p = self.connect()
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(8192).decode()
        except:
            print("Network error!")

    def disconnect(self):
        self.client.close(self.addr)

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return pickle.loads(self.client.recv(8192))
        except Exception as e:
            print(e)
