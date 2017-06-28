import datetime
import logging
from multiprocessing.dummy import Value
import os
from queue import Queue
from threading import Thread, Lock


from common import KindOfStorage, Counter, Registry
from sync_worker import Parser

workers_number = 15

entering_url = 'https://docs.python.org/3.6/'
prefix = 'https://docs.python.org/3.6/'


def main():
    try:
        os.remove('data.txt')
    except Exception:
        pass

    t1 = datetime.datetime.utcnow()

    storage = KindOfStorage(Lock(), Value('i', 0))
    counter = Counter(Lock(), Value('i', 0))
    registry = Registry(Lock(), dict())

    urls_queue = Queue()

    counter.up()
    urls_queue.put([entering_url, 3])

    parsers = [Thread(target=Parser(storage, counter, registry, prefix,
                                     workers_number, urls_queue).run)
               for _ in range(workers_number)]

    [p.start() for p in parsers]
    [p.join() for p in parsers]

    logging.info(datetime.datetime.utcnow() - t1)


if __name__ == '__main__':
    main()
