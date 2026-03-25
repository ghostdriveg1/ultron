# T5 — Memory Infrastructure Connections

## Context
Connects Ultron to Upstash Redis (hot memory) and Zilliz (vector memory). All memory operations flow through these connections. Must be bulletproof — memory failure = Ultron loses context.

**Dependencies:** T1  
**Blocks:** T8 (key rotation needs Redis), T18 (memory write needs both)

## Files to Create
| File | Purpose |
|---|---|
| `packages/memory/redis_client.py` | Upstash Redis connection |
| `packages/memory/zilliz_client.py` | Zilliz multi-account client |
| `packages/memory/health_monitor.py` | Connection health checking |
| `packages/memory/fallback_manager.py` | Graceful degradation |

## Implementation Plan

### Redis Client
```python
from upstash_redis import Redis
from typing import Optional, Any
import json

class UltronRedisClient:
    """
    Primary hot memory client.
    Stores: context passports, key pool status, 
            core memory, circuit breaker states.
    """
    
    def __init__(self, url: str, token: str):
        self.client = Redis(url=url, token=token)
        self.fallback_cache = {}  # In-memory fallback
    
    async def get_passport(self, task_id: str) -> Optional[dict]:
        """Retrieve context passport for task restoration."""
        try:
            data = await self.client.get(f"passport:{task_id}")
            return json.loads(data) if data else None
        except Exception:
            return self.fallback_cache.get(f"passport:{task_id}")
    
    async def save_passport(self, task_id: str, passport: dict, ttl: int = 3600):
        """Save context passport with TTL."""
        try:
            await self.client.setex(
                f"passport:{task_id}", 
                ttl,
                json.dumps(passport)
            )
            self.fallback_cache[f"passport:{task_id}"] = passport
        except Exception as e:
            self.fallback_cache[f"passport:{task_id}"] = passport
```

### Zilliz Multi-Account Client
```python
class ZillizMultiAccountClient:
    """
    Manages 15 Zilliz accounts transparently.
    Routes writes to account with most free space.
    Routes reads to account where data exists.
    """
    
    def __init__(self, accounts: list[dict]):
        # accounts = [{"uri": "...", "token": "..."}, ...]
        self.connections = [
            MilvusClient(uri=acc["uri"], token=acc["token"])
            for acc in accounts
        ]
        self.usage_tracker = {}  # account_index → vectors_stored
    
    async def insert(self, collection: str, data: list[dict]) -> bool:
        """Insert into account with most free space."""
        target = self._get_least_used_account()
        try:
            self.connections[target].insert(
                collection_name=collection,
                data=data
            )
            self.usage_tracker[target] = self.usage_tracker.get(target, 0) + len(data)
            return True
        except Exception:
            # Try next account
            return await self._insert_with_fallback(collection, data, exclude=target)
    
    async def search(self, collection: str, query_vector: list, limit: int = 10) -> list:
        """Search across all accounts, merge results."""
        all_results = []
        for conn in self.connections:
            try:
                results = conn.search(
                    collection_name=collection,
                    data=[query_vector],
                    limit=limit
                )
                all_results.extend(results[0])
            except Exception:
                continue  # Skip failed account
        
        # Sort by score, deduplicate, return top-k
        return sorted(all_results, key=lambda x: x['distance'])[:limit]
```

## Acceptance Criteria
- [ ] Redis read/write latency < 5ms (99th percentile)
- [ ] Zilliz search returns results in < 50ms
- [ ] If one Zilliz account fails: others continue serving
- [ ] If Redis fails: falls back to in-memory cache
- [ ] Connection health reported to dashboard
- [ ] Automatic reconnect on dropped connections

## Edge Cases
- All Zilliz accounts fail simultaneously: use in-memory FAISS fallback
- Redis connection timeout: increase timeout, retry 3×, then use local dict
- Zilliz collection not found: auto-create with correct schema
