import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union, Optional

from aioredis import from_url
from asphalt.core import Component, Context, context_teardown, merge_config
from async_generator import yield_
from typeguard import check_argument_types

logger = logging.getLogger(__name__)


class RedisComponent(Component):
    """
    Creates one or more :class:`aioredis.Redis` resources.

    If ``connections`` is given, a Redis client resource will be published for each key in the
    dictionary, using the key as the resource name. Any extra keyword arguments to the component
    constructor will be used as defaults for omitted configuration values.

    If ``connections`` is omitted, a single Redis client resource (``default`` / ``ctx.redis``)
    is published using any extra keyword arguments passed to the component.

    The client(s) will not connect to the target database until they're used for the first time.

    :param connections: a dictionary of resource name ⭢ :meth:`configure_client` arguments
    :param default_client_args: default values for omitted :meth:`configure_client`
        arguments
    """

    def __init__(self, connections: Dict[str, Dict[str, Any]] = None, **default_client_args):
        assert check_argument_types()
        if not connections:
            default_client_args.setdefault('context_attr', 'redis')
            connections = {'default': default_client_args}

        self.clients = []  # type: List[Tuple[str, str, dict]]
        for resource_name, config in connections.items():
            config = merge_config(default_client_args, config or {})
            context_attr = config.pop('context_attr', resource_name)
            client_args = self.configure_client(**config)
            self.clients.append((resource_name, context_attr, client_args))

    @classmethod
    def configure_client(
            cls, address: Union[str, Path] = 'localhost', port: int = 6379,
            db: int = 0, username: Optional[str] = None, password: Optional[str] = None,
            ssl: bool = False, **client_args) -> Dict[str, Any]:
        """
        Configure a Redis client.

        :param address: IP address, host name or path to a UNIX socket
        :param port: port number to connect to (ignored for UNIX sockets)
        :param db: database number to connect to
        :param username: username used if the server requires authentication
        :param password: password used if the server requires authentication
        :param ssl: ``True`` to enable TLS when connecting to the server.
            See the aioredis documentation for more SSL options.
        :param client_args: extra keyword arguments passed to :func:`~aioredis.create_redis_pool`

        """
        assert check_argument_types()
        if username or password:
            credentials = f'{username or ""}:{password or ""}@'
        else:
            credentials = ''

        if isinstance(address, Path) or address.startswith('/'):
            client_args['url'] = f'unix://{credentials}{address}?db={db}'
        else:
            scheme = 'rediss' if ssl else 'redis'
            client_args['url'] = f'{scheme}://{credentials}{address}:{port}/{db}'

        return client_args

    @context_teardown
    async def start(self, ctx: Context):
        clients = []
        for resource_name, context_attr, config in self.clients:
            redis = from_url(**config)
            clients.append((resource_name, redis))
            ctx.add_resource(redis, resource_name, context_attr)
            logger.info('Configured Redis client (%s / ctx.%s; url=%s)', resource_name,
                        context_attr, config['url'])

        await yield_()

        for resource_name, redis in clients:
            await redis.close()
            await redis.connection_pool.disconnect()
            logger.info('Redis client (%s) shut down', resource_name)
