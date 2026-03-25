import json
from packages.infrastructure.redis_client import UltronRedis

class ProgressEntropyDetector:
    def __init__(self, agent_id: str, redis: UltronRedis):
        self.agent_id = agent_id
        self.redis = redis
        self.history_key = f"entropy_history:{agent_id}"

    async def is_loop(self, tokens_used: int, progress: float) -> bool:
        entry = json.dumps({"tokens": tokens_used, "progress": progress})
        await self.redis.lpush(self.history_key, entry)
        await self.redis.ltrim(self.history_key, 0, 9)
        
        history = await self.redis.lrange(self.history_key, 0, 9)
        if len(history) < 5:
            return False
            
        parsed_history = [json.loads(h) for h in history]
        parsed_history.reverse() # chronological: oldest to newest
        
        token_delta = parsed_history[-1]["tokens"] - parsed_history[-5]["tokens"]
        progress_delta = parsed_history[-1]["progress"] - parsed_history[-5]["progress"]
        
        return token_delta > 5000 and progress_delta < 1.0
