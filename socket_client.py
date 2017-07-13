from multiprocessing import Pool
import socket

import logging

import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(process)-6s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')


HOST = '127.0.0.1'
PORT = 5007


def client(i):
    t1 = datetime.datetime.utcnow()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        logging.info(f'request {i:4}, started')
        s.connect((HOST, PORT))
        received = 0

        while True:
            data = s.recv(1024)

            if not data:
                logging.info(f'request {i:4}, received: {received:10,}, time: {datetime.datetime.utcnow() - t1}')
                return

            received += len(data)


def load():
    t1 = datetime.datetime.utcnow()
    pool = Pool(400)

    pool.map(client, range(10_000))

    logging.info(f'total time: {datetime.datetime.utcnow() - t1}')


if __name__ == '__main__':
    load()
