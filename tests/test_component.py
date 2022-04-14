import logging
import os

import pytest
from asphalt.core.context import Context
from redis.asyncio import Redis

from asphalt.redis.component import RedisComponent


@pytest.mark.asyncio
async def test_default_connection(caplog):
    """Test that the default connection is started and is available on the context."""
    caplog.set_level(logging.INFO)
    async with Context() as context:
        await RedisComponent(port=63790).start(context)
        context.require_resource(Redis)

    records = [
        record for record in caplog.records if record.name == "asphalt.redis.component"
    ]
    records.sort(key=lambda r: r.message)
    assert len(records) == 2
    assert records[0].message == (
        "Configured Redis client (default; host='localhost', port=63790)"
    )
    assert records[1].message == "Redis client (default) shut down"


@pytest.mark.asyncio
async def test_unix_socket_connection(caplog):
    """Test that the default connection is started and is available on the context."""
    caplog.set_level(logging.INFO)
    async with Context() as context:
        component = RedisComponent(unix_socket_path='/tmp/foo', validate_connection=False)
        await component.start(context)
        context.require_resource(Redis)

    records = [
        record for record in caplog.records if record.name == "asphalt.redis.component"
    ]
    records.sort(key=lambda r: r.message)
    assert len(records) == 2
    assert records[0].message == (
        "Configured Redis client (default; path='/tmp/foo')"
    )
    assert records[1].message == "Redis client (default) shut down"


@pytest.mark.asyncio
async def test_create_remove_key():
    """Test the client against a real Redis server."""
    async with Context() as context:
        component = RedisComponent(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=os.getenv("REDIS_PORT", 63790),
        )
        await component.start(context)
        redis = context.require_resource(Redis)
        await redis.set("key", b"value")
        assert await redis.get("key") == b"value"
