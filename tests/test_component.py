import logging
import os

import pytest
from aioredis import Redis
from asphalt.core.context import Context

from asphalt.redis.component import RedisComponent

REDIS_HOSTNAME = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 63790)


@pytest.mark.asyncio
async def test_default_connection(caplog):
    """Test that the default connection is started and is available on the context."""
    caplog.set_level(logging.INFO)
    async with Context() as context:
        await RedisComponent(port=63790).start(context)
        assert isinstance(context.redis, Redis)

    records = [record for record in caplog.records if record.name == 'asphalt.redis.component']
    records.sort(key=lambda r: r.message)
    assert len(records) == 2
    assert records[0].message == ("Configured Redis client (default / ctx.redis; "
                                  "url=redis://localhost:63790/0)")
    assert records[1].message == 'Redis client (default) shut down'


@pytest.mark.asyncio
async def test_multiple_connections(caplog):
    """Test that a multiple connection configuration works as intended."""
    caplog.set_level(logging.INFO)
    async with Context() as context:
        await RedisComponent(connections={
            'db1': {'address': REDIS_HOSTNAME, 'port': REDIS_PORT},
            'db2': {'address': REDIS_HOSTNAME, 'port': REDIS_PORT, 'db': 2}
        }).start(context)
        assert isinstance(context.db1, Redis)
        assert isinstance(context.db2, Redis)

    records = [record for record in caplog.records if record.name == 'asphalt.redis.component']
    records.sort(key=lambda r: r.message)
    assert len(records) == 4
    assert records[0].message == ("Configured Redis client (db1 / ctx.db1; "
                                  f"url=redis://{REDIS_HOSTNAME}:{REDIS_PORT}/0)")
    assert records[1].message == ("Configured Redis client (db2 / ctx.db2; "
                                  f"url=redis://{REDIS_HOSTNAME}:{REDIS_PORT}/2)")
    assert records[2].message == 'Redis client (db1) shut down'
    assert records[3].message == 'Redis client (db2) shut down'


@pytest.mark.asyncio
async def test_create_remove_key():
    """Test the client against a real Redis server."""
    async with Context() as context:
        await RedisComponent(address=REDIS_HOSTNAME, port=REDIS_PORT).start(context)
        await context.redis.set('key', b'value')
        assert await context.redis.get('key') == b'value'
