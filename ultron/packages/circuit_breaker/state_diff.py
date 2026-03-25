import hashlib
from git import Repo
from packages.infrastructure.redis_client import UltronRedis

class StateDiffMonitor:
    def __init__(self, agent_id: str, redis: UltronRedis):
        self.agent_id = agent_id
        self.redis = redis
        self.hash_key = f"state_hashes:{agent_id}"

    async def is_loop(self) -> bool:
        repo = Repo(".")
        diff_output = repo.git.diff("HEAD", stat=True)
        current_hash = hashlib.md5(diff_output.encode()).hexdigest()
        
        history = await self.redis.lrange(self.hash_key, 0, 2)
        
        await self.redis.lpush(self.hash_key, current_hash)
        await self.redis.ltrim(self.hash_key, 0, 2)
        
        if len(history) == 3 and all(h == current_hash for h in history):
            return True
        return False
