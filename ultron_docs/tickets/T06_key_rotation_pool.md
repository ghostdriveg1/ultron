# T6 — Key Rotation Pool + Quota Brain

## Context
THE most critical infrastructure component. This is Ultron's lifeblood. Without this, Ultron dies when any single API key exhausts. With this, Ultron has effectively unlimited quota across all providers. Zero interruption. Ever.

**Dependencies:** T1, T5  
**Blocks:** T9 (MoA needs keys), T10 (Instant mode needs keys)

**THIS IS ONE OF THE 5 HARDEST TICKETS — USE TRAYCER**

## Files to Create
| File | Purpose |
|---|---|
| `packages/brain/key_rotation/pool.py` | Core key selection algorithm |
| `packages/brain/key_rotation/quota_brain.py` | Usage tracking + prediction |
| `packages/brain/key_rotation/admission_control.py` | Token bucket rate limiter |
| `packages/brain/key_rotation/key_loader.py` | Load keys from Cloudflare KV |

## Implementation Plan

### Key Pool (pool.py)
```python
import heapq
import time
from dataclasses import dataclass, field
from typing import Optional
import asyncio

@dataclass(order=True)
class APIKey:
    """Represents one API key with its quota state."""
    quota_remaining: int = field(compare=True)
    reset_time: float = field(compare=False)
    key_value: str = field(compare=False)
    provider: str = field(compare=False)
    model: str = field(compare=False)
    key_id: str = field(compare=False)
    is_available: bool = field(default=True, compare=False)

class KeyRotationPool:
    """
    O(log n) key selection using max-heap sorted by quota_remaining.
    
    Ghost pastes keys via website → stored in Cloudflare KV →
    loaded here → managed in sorted heap →
    rotated transparently when exhausted.
    
    SACRED FILE: Never auto-modified by self-modification engine.
    """
    
    def __init__(self, redis_client, kv_client):
        self.redis = redis_client
        self.kv = kv_client
        self.pools: dict[str, list[APIKey]] = {}  # provider → heap
        self._locks: dict[str, asyncio.Lock] = {}
    
    async def initialize(self):
        """Load all keys from Cloudflare KV on startup."""
        # Load all stored keys
        # Build heaps per provider
        # Start background quota refresh task
        pass
    
    async def get_key(self, provider: str, model: str) -> Optional[str]:
        """
        Select best available key for provider+model.
        O(log n) heap operation.
        
        Returns API key string, or None if all exhausted.
        Side effect: pre-warms next key in background.
        """
        async with self._get_lock(provider):
            heap = self.pools.get(provider, [])
            
            while heap:
                # Peek at best key (most quota remaining)
                best = heap[0]
                
                if not best.is_available:
                    heapq.heappop(heap)
                    continue
                
                if best.quota_remaining <= 0:
                    # Check if reset time has passed
                    if time.time() >= best.reset_time:
                        best.quota_remaining = self._get_daily_limit(provider)
                        heapq.heapreplace(heap, best)
                        continue
                    else:
                        heapq.heappop(heap)
                        continue
                
                # Pre-warm next key in background
                if best.quota_remaining < 50:
                    asyncio.create_task(self._pre_warm_next(provider))
                
                return best.key_value
            
            return None  # All keys exhausted
    
    async def report_exhausted(self, key_value: str, provider: str):
        """Called when 429 received. Mark key unavailable."""
        # Find key in heap
        # Mark is_available = False
        # Save checkpoint to Redis immediately
        # Emit metric to monitoring
        pass
    
    async def report_usage(self, key_value: str, tokens_used: int):
        """Update quota tracking after each API call."""
        # Update quota_remaining in heap
        # Save to Redis for persistence
        pass
    
    def _get_daily_limit(self, provider: str) -> int:
        limits = {
            "google": 1000,      # Gemini Pro per account
            "groq": 14400,       # Very high
            "cerebras": 100000,  # Extremely high
            "openrouter": 500,
            "together": 1000,
            "puter": 100
        }
        return limits.get(provider, 500)
```

### Quota Brain (quota_brain.py)
```python
class QuotaBrain:
    """
    Monitors all API quotas in real-time.
    Predicts exhaustion before it happens.
    Auto-scales thinking depth based on available quota.
    
    SACRED FILE: Never auto-modified.
    """
    
    def get_thinking_depth(self) -> dict:
        """
        Returns optimal thinking configuration based on quota.
        Called before every task to set MoA parameters.
        """
        total_available = self._calculate_total_quota()
        
        if total_available > 20000:
            return {
                "proposers": 8,
                "self_consistency": 10,
                "constitutional_rounds": 3,
                "research": True,
                "alphaevolve": True,
                "mode": "MAXIMUM_QUALITY"
            }
        elif total_available > 10000:
            return {
                "proposers": 8,
                "self_consistency": 5,
                "constitutional_rounds": 2,
                "research": "complex_only",
                "alphaevolve": "coding_only",
                "mode": "HIGH_QUALITY"
            }
        elif total_available > 5000:
            return {
                "proposers": 5,
                "self_consistency": 3,
                "constitutional_rounds": 1,
                "research": False,
                "alphaevolve": False,
                "mode": "GOOD_QUALITY"
            }
        else:
            # Alert Ghost
            asyncio.create_task(self._alert_low_quota())
            return {
                "proposers": 1,
                "self_consistency": 1,
                "constitutional_rounds": 0,
                "research": False,
                "mode": "EMERGENCY"
            }
```

### Admission Control (admission_control.py)
```python
class TokenBucketAdmissionControl:
    """
    Prevents hitting rate limits proactively.
    Uses token bucket algorithm per provider.
    
    Instead of hitting 429 and recovering:
    predict exhaustion and switch BEFORE it happens.
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
        # Rates per provider (requests per minute)
        self.rates = {
            "google": 15,
            "groq": 100,
            "cerebras": 500,
            "openrouter": 20
        }
    
    async def can_proceed(self, provider: str) -> bool:
        """Check if we can make a request without hitting rate limit."""
        current_rpm = await self._get_current_rpm(provider)
        limit = self.rates.get(provider, 10)
        return current_rpm < limit * 0.85  # 85% threshold
    
    async def wait_if_needed(self, provider: str) -> float:
        """Returns seconds to wait (0 if can proceed immediately)."""
        if await self.can_proceed(provider):
            return 0.0
        
        # Calculate wait time
        current_rpm = await self._get_current_rpm(provider)
        limit = self.rates.get(provider, 10)
        # Exponential backoff
        return min(60.0, (current_rpm / limit) ** 2)
```

## Acceptance Criteria
- [ ] Key rotation completes in < 55ms after 429
- [ ] O(log n) key selection verified with timing tests
- [ ] With 20 Gemini keys: 20x quota confirmed
- [ ] Quota prediction accurate to within 10%
- [ ] Thinking depth auto-adjusts when quota low
- [ ] All key values encrypted in storage, never logged
- [ ] Adding new key via website → live in pool within 5 seconds
- [ ] Key pool survives ClawCloud restart (state in Redis)

## Edge Cases
- ALL keys across ALL providers exhausted: send Discord alert, queue tasks for midnight reset
- Key suddenly works again (provider extended quota): detect on next use, re-add to pool
- Clock drift causes reset time miscalculation: use provider's actual reset time from 429 response header
- New key added mid-task: added to pool immediately, available for next request
