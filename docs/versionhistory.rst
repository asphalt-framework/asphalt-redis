Version history
===============

This library adheres to `Semantic Versioning 2.0 <http://semver.org/>`_.

**UNRELEASED**

- Removed explicit run-time argument type checks and the ``typeguard`` dependency

**4.0.0** (2022-04-14)

- **BACKWARD INCOMPATIBLE** Upgraded Asphalt dependency to ~4.7
- **BACKWARD INCOMPATIBLE** Switched backing library from aioredis to the official
  redis-py (which now has asyncio support)
- **BACKWARD INCOMPATIBLE** Refactored component to only provide a single Redis client
  (you will have to add two components to get two clients)
- **BACKWARD INCOMPATIBLE** Dropped the context attribute (use dependency injection
  instead)

**3.0.1** (2022-04-14)

- Fixed overly restrictive dependency constraint on Asphalt core

**3.0.0** (2021-12-27)

- **BACKWARD INCOMPATIBLE** Upgraded aioredis dependency to ~2.0
- Added support for Python 3.10
- Dropped support for Python 3.5 and 3.6

**2.1.1** (2019-01-04)

- Unpinned aioredis dependency to allow upgrading from v1.0 (the version pinning was an accident)

**2.1.0** (2018-12-16)

- Updated to work with aioredis 1.0+

**2.0.1** (2017-06-04)

- Added compatibility with Asphalt 4.0
- Added Docker configuration for easier local testing

**2.0.0** (2017-04-10)

- **BACKWARD INCOMPATIBLE** Migrated to Asphalt 3.0

**1.0.0** (2016-05-16)

- Initial release
