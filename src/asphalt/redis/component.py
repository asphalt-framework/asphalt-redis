from __future__ import annotations

import logging

from typeguard import check_argument_types

from asphalt.core import Component, Context, context_teardown
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class RedisComponent(Component):
    """
    Provides a :class:`redis.asyncio.Redis` client as a resource.

    :param resource_name: name of the client resource to be added
    :param validate_connection: if true, check that the server can be connected to
        before adding the client resource
    :param kwargs: keyword arguments passed to :class:`redis.asyncio.Redis`
    """

    def __init__(
        self,
        *,
        resource_name: str = "default",
        validate_connection: bool = True,
        **kwargs,
    ):
        check_argument_types()
        self.resource_name = resource_name
        self.validate_connection = validate_connection
        self.client = Redis(**kwargs)

    @context_teardown
    async def start(self, ctx: Context) -> None:
        async with self.client:
            if self.validate_connection:
                await self.client.ping()

            ctx.add_resource(self.client, self.resource_name)

            connection_kwargs = self.client.connection_pool.connection_kwargs
            if "unix_socket_path" in connection_kwargs:
                params = f"connection_kwargs={connection_kwargs['unix_socket_path']!r}"
            else:
                params = (
                    f"host={connection_kwargs.get('host', 'localhost')!r}, "
                    f"port={connection_kwargs.get('port', 6379)}"
                )

            logger.info(
                "Configured Redis client (%s; %s)",
                self.resource_name,
                params,
            )

            yield

        logger.info("Redis client (%s) shut down", self.resource_name)
