# -*- coding: utf-8 -*-
"""
    spider
    ~~~~~~

    Main interface for starting the crawler

    :copyright: (c) 2018, Matthias Riegler,
    :license: GPLv3, see LICENSE.md for more details.
"""
import logging
import multiprocessing as mp
import uvloop
from . import Spider


# Set loglevel to info
logging.basicConfig(level=logging.INFO)


def create_spider():
    loop = uvloop.new_event_loop()
    Spider(loop=loop, num_tasks=1)

    return mp.Process(target=loop.run_forever)


if __name__ == "__main__":

    processes = []

    for _ in range(mp.cpu_count()):
        processes.append(create_spider())

    for process in processes:
        process.start()

    input(" -> Press enter to exit")
    for process in processes:
        process.terminate()
