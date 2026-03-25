import os
import time
from typing import Dict
from .servers import ALL_SERVERS

class AuthManager:
    """Manages MCP server authentication with short-lived memory caching."""
    def __init__(self):
        self._cache: Dict[str, dict] = {}
        self._cache_expiry: Dict[str, float] = {}
        self._ttl = 60.0 # 60s TTL

        # Map server names to config
        self._servers = {s.name: s for s in ALL_SERVERS}

    def get_auth_headers(self, server_name: str) -> dict:
        now = time.time()
        
        # Check cache
        if server_name in self._cache and now < self._cache_expiry.get(server_name, 0):
            return self._cache[server_name]
            
        server_config = self._servers.get(server_name)
        if not server_config:
            return {}
            
        headers = {}
        if server_config.auth_env_var:
            token = os.getenv(server_config.auth_env_var)
            if token:
                headers["Authorization"] = f"Bearer {token}"
                
        # Update cache
        self._cache[server_name] = headers
        self._cache_expiry[server_name] = now + self._ttl
        
        return headers
