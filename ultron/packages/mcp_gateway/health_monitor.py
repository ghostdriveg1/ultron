import asyncio
import time
import httpx
from packages.infrastructure.redis_client import UltronRedis
from .servers import ALL_SERVERS

class MCPHealthMonitor:
    """Monitors the health of MCP servers and updates Redis."""
    def __init__(self, redis: UltronRedis):
        self.redis = redis
        self.interval = 60
        self._task = None
        self._servers = {s.name: s.url for s in ALL_SERVERS}

    async def start_monitoring(self):
        """Starts the background monitoring loop."""
        if self._task is None:
            self._task = asyncio.create_task(self._monitor_loop())

    async def _monitor_loop(self):
        while True:
            for name, url in self._servers.items():
                status = "HEALTHY"
                error = ""
                try:
                    # Ping /health or root depending on generic MCP server implementation
                    # MCP doesn't strictly dictate /health but it's common
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        # Assuming a standard /health endpoint for these servers
                        health_url = url.rstrip('/') + '/health'
                        res = await client.get(health_url)
                        if res.status_code >= 400:
                            status = "UNHEALTHY"
                            error = f"HTTP {res.status_code}"
                except Exception as e:
                    status = "UNHEALTHY"
                    error = str(e)
                    
                data = {
                    "status": status,
                    "last_check": time.time(),
                    "error": error
                }
                
                await self.redis.set(f"mcp_health:{name}", str(data))
                
                # If UNHEALTHY, we could disable tools in registry here, 
                # but currently we just log it. The client will check status.
                
            await asyncio.sleep(self.interval)

    async def get_status(self, server_name: str) -> str:
        data_str = await self.redis.get(f"mcp_health:{server_name}")
        if not data_str:
            return "UNKNOWN"
            
        try:
            import ast
            data = ast.literal_eval(data_str.decode() if isinstance(data_str, bytes) else data_str)
            return data.get("status", "UNKNOWN")
        except:
            return "UNKNOWN"
