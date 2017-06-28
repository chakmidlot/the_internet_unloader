from multiprocessing.dummy import Value

import aiohttp
import datetime
import asyncio
import logging
import os
import socket
import traceback

from common import parse_page, KindOfStorage, Counter, Registry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


entering_url = 'https://docs.python.org/3.6/'
prefix = 'https://docs.python.org/3.6/'


class FakeLock():

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


storage = KindOfStorage(FakeLock(), Value('i', 0))
counter = Counter(FakeLock(), Value('i', 0))
registry = Registry(FakeLock(), dict())


semaphore = asyncio.Semaphore(15)


async def main(loop):
    counter.up()
    registry.add(entering_url)

    connector = aiohttp.TCPConnector(family=socket.AF_INET)
    session = aiohttp.ClientSession(connector=connector)
    await recursive_load(entering_url, loop, session)


async def recursive_load(url, loop, http_session, remain_attempts=3):
    async with semaphore:
        logging.info(f'attempts {remain_attempts}; scheduling {url}')

        try:
            page = await fetch(http_session, url)
            logging.info(f'processing {url}')

            body, urls = parse_page(url, page, prefix)

            storage.save(url, body)

            for url in urls:
                if registry.add(url):
                    counter.up()
                    asyncio.ensure_future(recursive_load(url, loop, http_session))

        except Exception:
            logging.info(traceback.format_exc())
            if not remain_attempts:
                logging.warning(f'{url} failed')
            else:
                counter.up()
                asyncio.ensure_future(recursive_load(url, loop, http_session, remain_attempts - 1))

        count = counter.down()
        if not count:
            http_session.close()
            loop.stop()


async def fetch(session, url):
    logging.info(f'waiting for {url}')
    async with session.get(url, timeout=60) as response:
        logging.info(f'loading {url}')
        return await response.text()


if __name__ == '__main__':
    try:
        os.remove('data.txt')
    except Exception:
        pass

    t1 = datetime.datetime.utcnow()

    loop = asyncio.get_event_loop()
    loop.create_task(main(loop))
    loop.run_forever()
    loop.close()

    logging.info(datetime.datetime.utcnow() - t1)
