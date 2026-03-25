"""
Ultron v3 — Connection Pool
Singleton manager for Redis and Zilliz connections.
Handles reconnection on failure and provides unified health reporting.
"""

import logging
import os
from typing import Optional

from packages.infrastructure.redis_client import UltronRedis
from packages.infrastructure.zilliz_client import ZillizPool
from packages.infrastructure import health_check

logger = logging.getLogger("ultron.pool")


class ConnectionPool:
    """
    Singleton connection pool for all infrastructure services.
    Caches instances and handles reconnection when unhealthy.
    """

    _instance: Optional["ConnectionPool"] = None
    _redis: Optional[UltronRedis] = None
    _zilliz: Optional[ZillizPool] = None

    def __new__(cls) -> "ConnectionPool":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_redis(self) -> UltronRedis:
        """
        Get the cached Redis instance. Reconnects if unhealthy.
        """
        if self._redis is None or not self._redis.is_healthy:
            url = os.getenv("UPSTASH_REDIS_REST_URL", "")
            token = os.getenv("UPSTASH_REDIS_REST_TOKEN", "")

            if not url or not token:
                raise RuntimeError(
                    "UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN must be set"
                )

            self._redis = UltronRedis(url=url, token=token)
            logger.info("Redis connection (re)established via ConnectionPool")

        return self._redis

    def get_zilliz(self) -> ZillizPool:
        """
        Get the cached ZillizPool instance.
        """
        if self._zilliz is None:
            self._zilliz = ZillizPool()
            logger.info("ZillizPool initialized via ConnectionPool")

        return self._zilliz

    async def health_report(self) -> dict:
        """
        Get combined health report for all infrastructure.
        """
        redis = self.get_redis()
        zilliz = self.get_zilliz()
        return await health_check.check_all(redis, zilliz)
