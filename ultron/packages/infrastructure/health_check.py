"""
Ultron v3 — Health Check
Pings Redis and all Zilliz accounts, returns combined health report.
"""

import logging
from typing import Any

from packages.infrastructure.redis_client import UltronRedis
from packages.infrastructure.zilliz_client import ZillizPool

logger = logging.getLogger("ultron.health")


async def check_all(
    redis: UltronRedis,
    zilliz: ZillizPool,
) -> dict[str, Any]:
    """
    Check health of all infrastructure components.

    Returns:
        {
            "redis": bool,
            "zilliz": { "account_1": bool, ..., "account_15": bool },
            "healthy_zilliz_count": int
        }
    """
    # Check Redis
    redis_healthy = redis.is_healthy
    try:
        await redis.get("health:ping")
        redis_healthy = True
    except Exception:
        redis_healthy = False

    # Check Zilliz
    zilliz_report = zilliz.get_health_report()
    healthy_count = sum(1 for v in zilliz_report.values() if v)

    result = {
        "redis": redis_healthy,
        "zilliz": zilliz_report,
        "healthy_zilliz_count": healthy_count,
    }

    logger.info(
        f"Health check: redis={redis_healthy}, "
        f"zilliz={healthy_count}/{len(zilliz_report)} healthy"
    )

    return result
