import logging
import traceback
import requests

from common import parse_page

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(process)-6s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')


class Parser:

    def __init__(self, storage, counter, registry, prefix, workers_number, queue):
        self.registry = registry
        self.counter = counter
        self.storage = storage
        self.prefix = prefix
        self.workers_number = workers_number
        self.queue = queue

    def run(self):
        while True:
            item = self.queue.get()

            if item is None:
                return

            url, remain_attempts = item

            try:
                self.process(url)
            except Exception:
                self.deal_with_exception(url, remain_attempts)

            count = self.counter.down()

            if not count:
                self.init_mass_termination()

    def process(self, url):
        page = self.load_page(url)
        body, urls = parse_page(url, page, self.prefix)
        self.populate_queue(urls)
        self.storage.save(url, body)

    def load_page(self, url):
        logging.debug(f'loading {url}')
        resp = requests.get(url)
        logging.info(f'done {url}')

        return resp.text

    def populate_queue(self, urls):
        for url in urls:
            if self.registry.add(url):
                self.counter.up()
                self.queue.put([url, 3])

    def deal_with_exception(self, url, remain_attempts):
        logging.info(traceback.format_exc())
        if not remain_attempts:
            logging.warning(f'failed {url}')
        else:
            self.counter.up()
            logging.warning(f'attempts {remain_attempts} of {url}')
            self.queue.put([url, remain_attempts - 1])

    def init_mass_termination(self):
        for i in range(self.workers_number):
            self.queue.put(None)
