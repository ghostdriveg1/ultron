import json
from typing import Optional
from packages.infrastructure.redis_client import UltronRedis

class ContextRestorer:
    def __init__(self, redis: UltronRedis):
        self.redis = redis

    async def save_checkpoint(self, task_id: str, state: dict) -> None:
        await self.redis.set(f"restore:{task_id}", json.dumps(state), ex=86400)

    async def restore(self, task_id: str) -> Optional[dict]:
        data = await self.redis.get(f"restore:{task_id}")
        if data:
            return json.loads(data)
        return None

    async def clear(self, task_id: str) -> None:
        await self.redis.delete(f"restore:{task_id}")
