import socket
import pickle
import configparser
config = configparser.ConfigParser()

class Network:
    def __init__(self):
        config.read('gameconfig.ini')
        self.addr = (config["Server"]["host"], int(config["Server"]["port"]))
        self.client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.client_socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)

    def connect(self):
        try:
            self.client_socket.connect(self.addr)
        except Exception as e:
            raise e

    def disconnect(self):
        self.client_socket.close()

    def send(self, data):
        try:
            self.client_socket.send(str.encode(data))
            return pickle.loads(self.client_socket.recv(4096))
        except Exception as e:
            print("Could not connect")
            print(e)
