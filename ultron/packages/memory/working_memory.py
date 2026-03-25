from packages.infrastructure.redis_client import UltronRedis

class WorkingMemory:
    def __init__(self, redis: UltronRedis):
        self.redis = redis

    async def add_turn(self, task_id: str, role: str, content: str) -> None:
        key = f"working_memory:{task_id}"
        entry = f"[{role.upper()}]: {content}"
        await self.redis.lpush(key, entry)
        await self.redis.ltrim(key, 0, 49)

    async def get_current(self, task_id: str) -> str:
        key = f"working_memory:{task_id}"
        lines = await self.redis.lrange(key, 0, 49)
        lines.reverse()
        return "\n".join(lines)

    async def clear(self, task_id: str) -> None:
        await self.redis.delete(f"working_memory:{task_id}")
