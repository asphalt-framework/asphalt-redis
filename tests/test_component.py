import ssl
from pathlib import Path

import pytest
from aioredis import Redis

from asphalt.core.context import Context
from asphalt.redis.component import RedisComponent


@pytest.mark.asyncio
async def test_default_connection(caplog):
    """Test that the default connection is started and is available on the context."""
    async with Context() as context:
        await RedisComponent().start(context)
        assert isinstance(context.redis, Redis)

    records = [record for record in caplog.records if record.name == 'asphalt.redis.component']
    records.sort(key=lambda r: r.message)
    assert len(records) == 2
    assert records[0].message == ("Configured Redis client (default / ctx.redis; "
                                  "address=('localhost', 6379), db=0)")
    assert records[1].message == 'Redis client (default) shut down'


@pytest.mark.asyncio
async def test_multiple_connections(caplog):
    """Test that a multiple connection configuration works as intended."""
    async with Context() as context:
        ssl_context = ssl.create_default_context()
        context.publish_resource(ssl_context)
        await RedisComponent(connections={
            'db1': {'address': Path('/tmp/redis.sock')},
            'db2': {'db': 2, 'ssl': 'default'}
        }).start(context)
        assert isinstance(context.db1, Redis)
        assert isinstance(context.db2, Redis)

    records = [record for record in caplog.records if record.name == 'asphalt.redis.component']
    records.sort(key=lambda r: r.message)
    assert len(records) == 4
    assert records[0].message == ("Configured Redis client (db1 / ctx.db1; "
                                  "address=/tmp/redis.sock, db=0)")
    assert records[1].message == ("Configured Redis client (db2 / ctx.db2; "
                                  "address=('localhost', 6379), db=2)")
    assert records[2].message == 'Redis client (db1) shut down'
    assert records[3].message == 'Redis client (db2) shut down'
