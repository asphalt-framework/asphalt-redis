Using the Redis connection
==========================

The published resource provides the `high level API`_ offered by aioredis.

The following snippet sets a key named ``somekey`` and then retrieves the key and makes sure the
value matches::

    async def handler(ctx):
        await ctx.redis.set('somekey', 'somevalue')
        assert await ctx.redis.get('somekey') == 'somevalue'


.. _high level API: https://aioredis.readthedocs.org/en/latest/mixins.html#aioredis-commands
