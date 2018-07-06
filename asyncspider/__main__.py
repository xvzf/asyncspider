# -*- coding: utf-8 -*-
"""
    spider
    ~~~~~~

    Main interface for starting the crawler

    :copyright: (c) 2018, Matthias Riegler,
    :license: GPLv3, see LICENSE.md for more details.
"""
import aioredis
import asyncio
import logging
import multiprocessing as mp
import uvloop
import click
from yarl import URL
from . import Spider


# Get logger
logger = logging.getLogger(__name__)

# Set loglevel to info
logging.basicConfig(level=logging.INFO)


@click.command()
@click.option("--num-threads",
              default=mp.cpu_count(),
              help="Number of multiprocessing threads")
@click.option("--num-tasks",
              default=10,
              help="Number of async crawlers for each thread")
@click.option("--redis-url",
              default="redis://localhost",
              help="Redis URL, you have to pass a common URL on each node if" +
                   " you want to run the crawler in a distributed manner")
@click.option("--start-url",
              default="",
              help="Where should we start..? :-)")
def run(num_threads, num_tasks, redis_url, start_url):
    """ Distributed web crawler based on uvloop, aiohttp and redis """

    async def add_start_url():
        """ Sets a start URL if requested """
        redis = await aioredis.create_redis(redis_url)
        await redis.sadd(Spider.TO_CRAWL_URLS, start_url)
        logger.info(f"Added {start_url} to the queue")

    def create_spider():
        """ Creats a spider object and sets the multiprocessing target """
        loop = uvloop.new_event_loop()
        Spider(loop=loop,
               num_tasks=num_tasks,
               redis_url=redis_url)
        return (mp.Process(target=loop.run_forever), loop)

    async def log_metrics():
        redis = await aioredis.create_redis(redis_url)
        start = await redis.scard(Spider.CRAWLED_URLS)
        while True:
            await asyncio.sleep(10)
            end = await redis.scard(Spider.CRAWLED_URLS)
            logging.info(f"Current scan rate: {(end-start) / 10} URLs/s")
            logging.info(f"URLs scanned: {end}")
            start = end

    processes = []

    for _ in range(num_threads):
        processes.append(create_spider())

    # Set start URL
    if URL(start_url).is_absolute():
        processes[0][1].run_until_complete(add_start_url())

    processes[0][1].create_task(log_metrics())

    for process, _ in processes:
        process.start()

    input(" -> Press enter to exit\n")
    for process in processes:
        process.terminate()


# Entrypoint
if __name__ == "__main__":
    run()
