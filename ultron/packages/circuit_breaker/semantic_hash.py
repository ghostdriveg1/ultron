import hashlib
import time
from packages.infrastructure.redis_client import UltronRedis

class SemanticHashRing:
    def __init__(self, agent_id: str, redis: UltronRedis):
        self.agent_id = agent_id
        self.redis = redis
        self.ring_key = f"action_ring:{agent_id}"

    def normalize_action(self, action: dict) -> str:
        tool = action.get("tool", "")
        target_type = action.get("target_type", "")
        operation = action.get("operation", "")
        fingerprint = f"{tool}:{target_type}:{operation}"
        return hashlib.sha256(fingerprint.encode()).hexdigest()[:16]

    async def is_loop(self, action: dict) -> bool:
        fingerprint = self.normalize_action(action)
        now_ms = int(time.time() * 1000)
        
        # Redis ZSET requires unique members. Encode timestamp to ensure duplicate fingerprints are allowed
        member = f"{fingerprint}:{now_ms}"
        await self.redis.zadd(self.ring_key, {member: now_ms})
        
        # 5-minute window
        window_start = now_ms - 300000
        recent = await self.redis.zrangebyscore(self.ring_key, window_start, "+inf")
        
        # Count occurrences of current fingerprint
        count = sum(1 for m in recent if m.startswith(fingerprint))
        
        # Trim ring (keep last 10)
        await self.redis.zremrangebyrank(self.ring_key, 0, -11)
        
        return count >= 3
