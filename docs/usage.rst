Using the Redis connection
==========================

The following snippet sets a key named ``somekey`` and then retrieves the key and makes
sure the value matches::

    from asphalt.core import Dependency, inject
    from redis.asyncio import Redis


    @inject
    async def handler(redis: Redis = Dependency()):
        await redis.set('somekey', 'somevalue')
        assert await redis.get('somekey') == 'somevalue'


.. seealso:: `Redis commands <https://redis-py.readthedocs.io/en/stable/commands.html>`_
