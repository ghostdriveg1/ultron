import json
import time
from packages.infrastructure.redis_client import UltronRedis

class ZepClient:
    def __init__(self, redis: UltronRedis):
        self.redis = redis

    async def add_episode(self, session_id: str, content: str, metadata: dict) -> str:
        key = f"zep:episodes:{session_id}"
        timestamp = int(time.time() * 1000)
        episode_id = f"ep_{timestamp}"
        
        entry = {
            "id": episode_id,
            "content": content,
            "metadata": metadata,
            "timestamp": timestamp
        }
        member = json.dumps(entry)
        
        await self.redis.zadd(key, {member: timestamp})
        return episode_id

    async def get_episodes(self, session_id: str, limit: int = 20) -> list[dict]:
        key = f"zep:episodes:{session_id}"
        members = await self.redis.zrevrange(key, 0, limit - 1)
        return [json.loads(m) for m in members]

    async def search_episodes(self, query: str, session_id: str) -> list[dict]:
        episodes = await self.get_episodes(session_id, limit=100)
        matches = [ep for ep in episodes if query.lower() in ep.get("content", "").lower()]
        return matches
