import time
import json
import httpx
from packages.infrastructure.redis_client import UltronRedis
from .auth_manager import AuthManager
from .health_monitor import MCPHealthMonitor
from .servers import ALL_SERVERS

class MCPServerUnavailableError(Exception):
    pass

class RateLimitExceededError(Exception):
    pass

class BifrostClient:
    """Client for routing and executing requests to MCP servers."""
    def __init__(self, auth_manager: AuthManager, health_monitor: MCPHealthMonitor, redis: UltronRedis):
        self.auth = auth_manager
        self.health = health_monitor
        self.redis = redis
        self._servers_config = {s.name: s for s in ALL_SERVERS}

    async def call(self, server_name: str, tool_name: str, params: dict) -> dict:
        start_time = time.time()
        
        # 1. Check health
        status = await self.health.get_status(server_name)
        if status == "UNHEALTHY":
            config = self._servers_config.get(server_name)
            if config and config.fallback:
                # Naive fallback routing
                server_name = config.fallback
                status = await self.health.get_status(server_name)
                if status == "UNHEALTHY":
                    raise MCPServerUnavailableError(f"Server {server_name} and fallback are UNHEALTHY")
            else:
                raise MCPServerUnavailableError(f"Server {server_name} is UNHEALTHY (no fallback)")
                
        # 5. Enforce rate limiting
        config = self._servers_config.get(server_name)
        limit = config.rate_limit_rpm if config else 600
        rpm_key = f"mcp_rpm:{server_name}"
        
        current_calls = await self.redis.incr(rpm_key)
        if current_calls == 1:
            await self.redis.expire(rpm_key, 60)
            
        if current_calls > limit:
            raise RateLimitExceededError(f"Rate limit exceeded for {server_name}")

        # 2. Get auth headers
        headers = await self.auth.get_auth_headers(server_name)
        headers["Content-Type"] = "application/json"
        
        url = config.url if config else f"http://localhost/{server_name}"
        
        # 3. POST tool call
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            },
            "id": int(time.time() * 1000)
        }
        
        success = True
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=30.0)
                response.raise_for_status()
                result = response.json()
                return result
        except Exception:
            success = False
            raise
        finally:
            # 4. Log
            duration_ms = int((time.time() - start_time) * 1000)
            log_entry = json.dumps({
                "server_name": server_name,
                "tool_name": tool_name,
                "duration_ms": duration_ms,
                "success": success
            })
            await self.redis.rpush("mcp_call_log", log_entry)
