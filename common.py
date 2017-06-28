import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def parse_page(base_url, page, prefix):
    try:
        soup = BeautifulSoup(page, 'html.parser')
        urls = [a.get('href') for a in soup.find_all('a')]

        guide_text = soup.text
        clean_guide_text = re.sub(r'\n+', '\n', guide_text)
        return clean_guide_text, map_and_filter_urls(base_url, urls, prefix)

    except Exception as e:
        raise Exception(base_url, str(page)[:100]) from e


def map_and_filter_urls(base_url, urls, prefix):
    for url in urls:
        full_url = urljoin(base_url, url)
        if full_url.startswith(prefix):
            cut_url = full_url.split('#')[0].split('?')[0]
            if cut_url.endswith('.html'):
                yield cut_url


class Counter:

    def __init__(self, lock, value):
        self.lock = lock

        self.value = value
        self.value.value = 0

    def up(self):
        with self.lock:
            self.value.value += 1
            logging.info(f'queued: {self.value.value}')
            return self.value.value

    def down(self):
        with self.lock:
            self.value.value -= 1
            logging.info(f'queued: {self.value.value}')
            return self.value.value

class KindOfStorage:

    def __init__(self, lock, value):
        self.lock = lock

        self.db_counter = value
        self.db_counter.value = 0

    def save(self, url, body):
        with self.lock:
            with open('data.txt', 'at') as db:
                db.write(f'{url} - {len(body)}\n')

            self.db_counter.value += 1
            logging.info(f'saved: {self.db_counter.value}')


class Registry:

    def __init__(self, lock, dictionary):
        self.lock = lock
        self.found_urls = dictionary

    def add(self, url):
        with self.lock:
            if url in self.found_urls:
                logging.debug(f'exists {url}')
                return False
            else:
                logging.debug(f'added {url}')
                self.found_urls[url] = True
                return True
