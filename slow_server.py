import socket
from random import Random
from time import sleep

from threading import Thread


HOST = ''
PORT = 5007


min_sleep_time = 0.1
max_sleep_time = 0.2


min_data_size = 100_000
max_data_size = 1_000_000

data = b'1234567890' * (max_data_size // 10)


class Server(Thread):

    def __init__(self, client, address):
        self.client = client
        self.address = address
        self.random = Random()
        super().__init__()

    def run(self):
        with self.client:
            print('Connected by', self.address)

            sleep(self.random.uniform(min_sleep_time, max_sleep_time))
            sending_data = data[:self.random.randint(min_data_size, max_data_size)]
            self.client.sendall(sending_data)


def listen():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()

            Server(conn, addr).start()


if __name__ == '__main__':
    listen()
