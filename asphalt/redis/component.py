import logging
from functools import partial
from pathlib import Path
from ssl import SSLContext
from typing import Dict, Any, Union

from aioredis import create_reconnecting_redis
from typeguard import check_argument_types

from asphalt.core import Component, Context, merge_config, resolve_reference

logger = logging.getLogger(__name__)


class RedisComponent(Component):
    """
    Publishes one or more :class:`aioredis.Redis` resources.

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

        self.clients = []
        for resource_name, config in connections.items():
            config = merge_config(default_client_args, config or {})
            config.setdefault('context_attr', resource_name)
            context_attr, client_args = self.configure_client(**config)
            self.clients.append((resource_name, context_attr, client_args))

    @classmethod
    def configure_client(cls, context_attr: str, address: Union[str, Path] = 'localhost',
                         port: int = 6379, db: int = 0, password: str = None,
                         ssl: Union[bool, str, SSLContext] = False, **client_args):
        """
        Configure a Redis client.

        :param context_attr: context attribute of the serializer (if omitted, the resource name
            will be used instead)
        :param address: IP address, host name or path to a UNIX socket
        :param port: port number to connect to (ignored for UNIX sockets)
        :param db: database number to connect to
        :param password: password used if the server requires authentication
        :param ssl: one of the following:

            * ``False`` to disable SSL
            * ``True`` to enable SSL using the default context
            * an :class:`ssl.SSLContext` instance
            * a ``module:varname`` reference to an :class:`~ssl.SSLContext` instance
            * name of an :class:`ssl.SSLContext` resource
        :param client_args: extra keyword arguments passed to
            :func:`~aioredis.create_reconnecting_redis`

        """
        assert check_argument_types()
        if isinstance(address, str) and not address.startswith('/'):
            address = (address, port)

        client_args.update({
            'address': address,
            'db': db,
            'password': password,
            'ssl': resolve_reference(ssl)
        })
        return context_attr, client_args

    @staticmethod
    async def shutdown_client(event, redis, resource_name):
        try:
            redis.close()
        except AttributeError:
            pass  # no connection has been established

        logger.info('Redis client (%s) shut down', resource_name)

    async def start(self, ctx: Context):
        for resource_name, context_attr, config in self.clients:
            # Resolve resource references
            if isinstance(config['ssl'], str):
                config['ssl'] = await ctx.request_resource(SSLContext, config['ssl'])

            redis = await create_reconnecting_redis(**config)
            ctx.finished.connect(
                partial(self.shutdown_client, redis=redis, resource_name=resource_name))
            ctx.publish_resource(redis, resource_name, context_attr)
            logger.info('Configured Redis client (%s / ctx.%s; address=%s, db=%d)', resource_name,
                        context_attr, config['address'], config['db'])
