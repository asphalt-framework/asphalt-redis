import logging
import os

import pytest
from _pytest.logging import LogCaptureFixture
from asphalt.core import Context, require_resource
from redis.asyncio import Redis

from asphalt.redis import RedisComponent

pytestmark = pytest.mark.anyio


async def test_default_connection(caplog: LogCaptureFixture) -> None:
    """Test that the default connection is started and is available on the context."""
    caplog.set_level(logging.INFO, "asphalt.redis")
    async with Context():
        await RedisComponent(port=63790).start()
        require_resource(Redis)

    records = sorted(caplog.records, key=lambda r: r.message)
    assert len(records) == 2
    assert records[0].message == (
        "Configured Redis client (default; host='localhost', port=63790)"
    )
    assert records[1].message == "Redis client (default) shut down"


async def test_unix_socket_connection(caplog: LogCaptureFixture) -> None:
    """Test that the default connection is started and is available on the context."""
    caplog.set_level(logging.INFO, "asphalt.redis")
    async with Context():
        component = RedisComponent(
            unix_socket_path="/tmp/foo", validate_connection=False
        )
        await component.start()
        require_resource(Redis)

    records = sorted(caplog.records, key=lambda r: r.message)
    assert len(records) == 2
    assert records[0].message == ("Configured Redis client (default; path='/tmp/foo')")
    assert records[1].message == "Redis client (default) shut down"


async def test_create_remove_key() -> None:
    """Test the client against a real Redis server."""
    async with Context():
        component = RedisComponent(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=os.getenv("REDIS_PORT", 63790),
        )
        await component.start()
        redis = require_resource(Redis)
        await redis.set("key", b"value")
        assert await redis.get("key") == b"value"
