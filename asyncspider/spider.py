# -*- coding: utf-8 -*-
"""
    spider
    ~~~~~~

    Async crawler

    :copyright: (c) 2018, Matthias Riegler,
    :license: GPLv3, see LICENSE.md for more details.
"""
import aioredis
import asyncio
import logging
import ssl
from aiohttp import (ClientSession,
                     ClientTimeout,
                     ClientError)
from lxml import html
from typing import ByteString
from yarl import URL


# Get logger
logger = logging.getLogger(__name__)


class Spider(object):
    """ Main class, magic happens here :-)

    :param loop: Eventloop
    :param num_tasks: How many async crawlers to start
    :param redis_url: Needed for distributed crawling
    :param tcp_timeout: Timeout for fetching an URL
    """

    TO_CRAWL_URLS = "asyncspider:pending"
    CRAWLED_URLS = "asyncspider:done"
    SLEEP_IF_NON_AVAIL = 0.1

    def __init__(
            self,
            loop: asyncio.AbstractEventLoop = None,
            num_tasks: int = 100,
            redis_url: str = "redis://localhost",
            tcp_timeout: int = 60):
        """ Init """
        self.loop = loop or asyncio.get_event_loop()
        self.redis_url = redis_url
        self.num_tasks = num_tasks

        # SSL context
        self.ssl_context = ssl.SSLContext()

        # Timeout
        self.timeout = ClientTimeout(tcp_timeout)

        self._tasks = []

        # Setup async stuff
        self.loop.run_until_complete(self._ainit())

    async def _ainit(self):
        """ Async init """
        # Connect to redis
        self.redis = await aioredis.create_redis(self.redis_url)

        # Spin up tasks :-)
        for i in range(self.num_tasks):
            self._tasks.append(self.loop.create_task(self.crawler()))
        logging.info(f"Started {self.num_tasks} crawlers")

    async def fetch(self, session: ClientSession, url: URL) -> ByteString:
        """ Fetches a URL """
        try:
            async with session.get(url, ssl=self.ssl_context) as response:
                return await response.read()
        except ssl.SSLError as se:
            logging.debug(se)
            return b""

    async def url_in_redis(self, url: str) -> bool:
        """ Checks if a URL was already crawled or it is in the queue """
        _rd_res = await self.redis.sismember(self.CRAWLED_URLS, url)
        _rd_res += await self.redis.sismember(self.TO_CRAWL_URLS, url)

        logging.debug(f"Redis result: {_rd_res == 0}")

        return _rd_res == 0

    async def extract_urls(self, url: URL, site: ByteString):
        """ Extracts URLs from an HTML site """
        dom = html.fromstring(site)
        for href in dom.xpath("//a/@href"):
            # This should work
            _url = str(url.join(URL(href)))

            if await self.url_in_redis(_url):
                logging.debug(f"Adding: {url}")
                await self.redis.sadd(self.TO_CRAWL_URLS, _url)
            else:
                logging.debug(f"{url} already done")

    async def crawler(self):
        """ Actual crawler, waits for a URL to be available in the redis
        set """
        logger.debug("Starting crawler...")
        async with ClientSession() as session:
            while True:
                url = await self.redis.spop(self.TO_CRAWL_URLS)

                if not url:
                    await asyncio.sleep(self.SLEEP_IF_NON_AVAIL)
                    continue
                else:
                    self.redis.sadd(self.CRAWLED_URLS, url)
                    url = URL(url.decode())

                try:
                    data = await self.fetch(session, url)
                    # Only do this when we are receiving something
                    if data:
                        await self.extract_urls(url=url, site=data)

                except ClientError as ce:
                    # Keep doing stuff
                    logging.debug(ce)

    def kill_all(self):
        """ Kills everything """

        for task in self._tasks:
            task.cancel()

        logger.info(f"Killed {len(self._tasks)} crawlers")
