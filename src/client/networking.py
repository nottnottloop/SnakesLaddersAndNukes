import socket
import pickle
import configparser
config = configparser.ConfigParser()

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        config.read('gameconfig.ini')
        self.host = config['Server']['host']
        self.port = int(config['Server']['port'])
        self.addr = (self.host, self.port)
        self.p = -1

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(4096).decode()
        except:
            print("Network error!")

    def disconnect(self):
        self.client.close(self.addr)

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return pickle.loads(self.client.recv(4096))
        except Exception as e:
            print(e)
