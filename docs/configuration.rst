Configuration
-------------

The typical Redis configuration using a single database at ``localhost`` on the default port,
database 0 would look like this:

.. code:: yaml

    components:
      redis:

The above configuration creates an automatically reconnecting :class:`~aioredis.Redis`
instance in the context, available as ``ctx.redis`` (resource name: ``default``).

If you wanted to connect to a database number 3 on ``redis.example.org``, you would do:

.. code:: yaml

    components:
      redis:
        address: redis.example.org
        db: 3

A more complex configuration creating two :class:`~aioredis.Redis` instances might look like:

.. code:: yaml

    components:
      redis:
        connections:
          db1:
            address: /tmp/redis.sock
            db: 2
          db2:
            port: 6380
            db: 1
            password: foobar

This configuration creates two :class:`~aioredis.Redis` resources, ``db1`` and ``db2`` (``ctx.db1``
and ``ctx.db2``) respectively.

.. seealso::
    Connection options: :func:`~asphalt.redis.component.RedisComponent.configure_client`
