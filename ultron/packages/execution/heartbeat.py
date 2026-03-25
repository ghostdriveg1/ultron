import asyncio
import time
from packages.infrastructure.redis_client import UltronRedis

class HeartbeatLoop:
    """Maintains a periodic ping to Redis to broadcast system health and liveness."""
    
    def __init__(self, redis: UltronRedis, node_id: str = "primary_ultron_node"):
        self.redis = redis
        self.node_id = node_id
        self.interval = 30 # Send heartbeat every 30s
        self.ttl = 45 # Expire if no heartbeat in 45s
        self._task = None

    async def start(self):
        if self._task is None:
            self._task = asyncio.create_task(self._loop())

    async def _loop(self):
        key = f"heartbeat:{self.node_id}"
        
        while True:
            try:
                # Set key with TTL for liveness
                await self.redis.set(key, str(time.time()), ex=self.ttl)
            except Exception as e:
                print(f"Failed to send heartbeat: {e}")
                
            await asyncio.sleep(self.interval)

    async def check_node_alive(self, node_id: str) -> bool:
        """Returns True if the specified node has sent a recent heartbeat."""
        val = await self.redis.get(f"heartbeat:{node_id}")
        return val is not None
