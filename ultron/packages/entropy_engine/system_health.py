from packages.infrastructure.redis_client import UltronRedis
from packages.infrastructure.zilliz_client import ZillizPool

class SystemHealthScorer:
    def __init__(self, redis: UltronRedis, zilliz: ZillizPool):
        self.redis = redis
        self.zilliz = zilliz

    async def score(self) -> float:
        try:
            val = await self.redis.get("health:ping")
            redis_healthy = val is not None or self.redis.is_healthy
        except Exception:
            redis_healthy = self.redis.is_healthy
            
        zilliz_healthy_count = self.zilliz.healthy_count
        accounts = getattr(self.zilliz, "_accounts", [1])
        zilliz_ratio = zilliz_healthy_count / max(1, len(accounts)) if accounts else 0.0
        
        health_score = 100.0
        if not redis_healthy:
            health_score -= 40
        health_score -= (1.0 - zilliz_ratio) * 30
        
        return max(0.0, health_score)
