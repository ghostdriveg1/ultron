import json
from typing import Optional
from packages.infrastructure.redis_client import UltronRedis

# Mock shared Task model for Phase 5 implementation
class Task:
    def __init__(self, id: str, description: str):
        self.id = id
        self.description = description

class EntropyScheduler:
    """Schedules tasks based on entropy scores using Redis Sorted Sets."""
    
    def __init__(self, redis: UltronRedis):
        self.redis = redis
        self.queue_key = "task_queue"

    async def enqueue(self, task: Task, entropy_score: float) -> None:
        """Adds a task to the priority queue scored by entropy."""
        task_json = json.dumps({"id": task.id, "description": task.description})
        
        # In Redis-py, mapping is {member: score}
        await self.redis.zadd(self.queue_key, {task_json: entropy_score})

    async def select_next(self) -> Optional[Task]:
        """Pops and returns the task with the highest entropy score."""
        # popmax removes and returns the highest scoring member
        results = await self.redis.zpopmax(self.queue_key, 1)
        
        if not results:
            return None
            
        task_str = results[0][0] if isinstance(results[0], tuple) else results[0]
        if isinstance(task_str, bytes):
            task_str = task_str.decode()
            
        data = json.loads(task_str)
        return Task(id=data["id"], description=data["description"])

    async def get_queue_depth(self) -> int:
        """Returns the number of tasks in the queue."""
        depth = await self.redis.zcard(self.queue_key)
        return depth or 0
