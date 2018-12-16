import logging
from pathlib import Path
from ssl import SSLContext
from typing import Dict, Any, Union, Tuple, List  # noqa: F401

from aioredis import create_redis_pool
from asphalt.core import Component, Context, merge_config, resolve_reference, context_teardown
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
            cls, address: Union[str, Tuple[str, int], Path] = 'localhost', port: int = 6379,
            db: int = 0, password: str = None, ssl: Union[bool, str, SSLContext] = False,
            **client_args) -> Dict[str, Any]:
        """
        Configure a Redis client.

        :param address: IP address, host name or path to a UNIX socket
        :param port: port number to connect to (ignored for UNIX sockets)
        :param db: database number to connect to
        :param password: password used if the server requires authentication
        :param ssl: one of the following:

            * ``False`` to disable SSL
            * ``True`` to enable SSL using the default context
            * an :class:`~ssl.SSLContext` instance
            * a ``module:varname`` reference to an :class:`~ssl.SSLContext` instance
            * name of an :class:`~ssl.SSLContext` resource
        :param client_args: extra keyword arguments passed to :func:`~aioredis.create_redis_pool`

        """
        assert check_argument_types()
        if isinstance(address, str) and not address.startswith('/'):
            address = (address, port)
        elif isinstance(address, Path):
            address = str(address)

        client_args.update({
            'address': address,
            'db': db,
            'password': password,
            'ssl': resolve_reference(ssl)
        })
        return client_args

    @context_teardown
    async def start(self, ctx: Context):
        clients = []
        for resource_name, context_attr, config in self.clients:
            # Resolve resource references
            if isinstance(config['ssl'], str):
                config['ssl'] = await ctx.request_resource(SSLContext, config['ssl'])

            redis = await create_redis_pool(**config)
            clients.append((resource_name, redis))
            ctx.add_resource(redis, resource_name, context_attr)
            logger.info('Configured Redis client (%s / ctx.%s; address=%s, db=%d)', resource_name,
                        context_attr, config['address'], config['db'])

        await yield_()

        for resource_name, redis in clients:
            try:
                redis.close()
                await redis.wait_closed()
            except AttributeError:
                pass  # no connection has been established

            logger.info('Redis client (%s) shut down', resource_name)
