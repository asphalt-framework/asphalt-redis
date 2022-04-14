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

A more complex configuration creating two :class:`redis.asyncio.Redis` instances might
look like::

    components:
      redis:
        resource_name: db1
        unix_socket_path: /tmp/redis.sock
        db: 2
      redis2:
        type: redis
        resource_name: db2
        port: 6380
        db: 1
        password: foobar

This configuration creates two :class:`redis.asyncio.Redis` resources, ``db1`` and
``db2``.
