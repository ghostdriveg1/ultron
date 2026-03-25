from packages.infrastructure.redis_client import UltronRedis
from typing import Any

class BugEntropyScorer:
    def __init__(self, redis: UltronRedis):
        self.redis = redis

    async def score(self) -> float:
        count_str = await self.redis.get("bug_log:count")
        bug_count = int(count_str) if count_str else 0
        return min(100.0, bug_count * 5.0)

    def sort_task_queue_by_bug_priority(self, tasks: list[Any]) -> list[Any]:
        return sorted(tasks, key=lambda t: getattr(t, "priority", 0) if hasattr(t, "priority") else 0, reverse=True)
