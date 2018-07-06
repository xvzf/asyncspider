ASYNCSPIDER
~~~~~~~~~~~


.. code-block::

    (venv) lola :: projects/random/asyncspider ‹master› % python -m asyncspider --help
    Usage: __main__.py [OPTIONS]

      Distributed web crawler based on uvloop, aiohttp and redis

    Options:
      --num-threads INTEGER  Number of multiprocessing threads
      --num-tasks INTEGER    Number of async crawlers for each thread
      --redis-url TEXT       Redis URL, you have to pass a common URL on each node
                             if you want to run the crawler in a distributed
                             manner
      --start-url TEXT       Where should we start..? :-)
      --help                 Show this message and exit.
