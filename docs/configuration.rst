Configuration
-------------

.. highlight:: yaml

The typical Redis configuration using a single database at ``localhost`` on the default
port, database 0 would look like this::

    components:
      redis:

The above configuration creates a :class:`redis.asyncio.Redis` resource with the name
``default``.

If you wanted to connect to a database number 3 on ``redis.example.org``, you would do::

    components:
      redis:
        host: redis.example.org
        db: 3
