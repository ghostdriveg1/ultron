import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from packages.circuit_breaker.breaker import CircuitBreaker, BreakerState
from packages.infrastructure.redis_client import UltronRedis

class MockUltronRedis:
    def __init__(self):
        self.data = {}
        self.lists = {}
        self.zsets = {}
        self.hashes = {}
        self.is_healthy = True

    async def get(self, key):
        return self.data.get(key)
        
    async def set(self, key, value, ex=None):
        self.data[key] = value
        
    async def hget(self, key, field):
        h = self.hashes.get(key, {})
        return h.get(field)

    async def hincrby(self, key, field, amount):
        if key not in self.hashes:
            self.hashes[key] = {}
        current = int(self.hashes[key].get(field, 0))
        new_val = current + amount
        self.hashes[key][field] = str(new_val)
        return new_val

    async def lpush(self, key, value):
        if key not in self.lists:
            self.lists[key] = []
        self.lists[key].insert(0, value)

    async def ltrim(self, key, start, stop):
        if key in self.lists:
            self.lists[key] = self.lists[key][start:stop+1]

    async def lrange(self, key, start, stop):
        if key in self.lists:
            if stop == -1:
                return self.lists[key][start:]
            return self.lists[key][start:stop+1]
        return []

    async def zadd(self, key, mapping):
        if key not in self.zsets:
            self.zsets[key] = {}
        for member, score in mapping.items():
            self.zsets[key][member] = score

    async def zrangebyscore(self, key, min_score, max_score):
        if key not in self.zsets:
            return []
        res = []
        for member, score in self.zsets[key].items():
            if score >= min_score:
                res.append(member)
        return res

    async def zremrangebyrank(self, key, start, stop):
        pass 

    async def delete(self, key):
        if key in self.data: del self.data[key]
        if key in self.lists: del self.lists[key]
        if key in self.zsets: del self.zsets[key]
        if key in self.hashes: del self.hashes[key]

@pytest.fixture
def mock_circuit_breaker():
    redis = MockUltronRedis()
    opus_caller = MagicMock()
    opus_caller.call = AsyncMock()
    discord = AsyncMock()
    
    cb = CircuitBreaker("agent_test", redis, opus_caller, discord)
    
    return cb

@pytest.mark.asyncio
async def test_semantic_loop(mock_circuit_breaker):
    action = {"tool": "read", "target_type": "file", "operation": "execute"}
    for _ in range(2):
        status = await mock_circuit_breaker.check(action, 10, 0.5)
        assert status == "PROCEED"
    
    status = await mock_circuit_breaker.check(action, 10, 0.5)
    assert status == "HALT" # trip count 1 auto recovers
    
    import json
    state_data = await mock_circuit_breaker.redis.get("circuit_breaker:agent_test")
    state = json.loads(state_data)
    assert state["trip_count"] == 1

@pytest.mark.asyncio
async def test_budget_exhaustion(mock_circuit_breaker):
    await mock_circuit_breaker.budget_guardian.consume(99990, "agent_test")
    action = {"tool": "read", "target_type": "complex_task", "operation": "execute"}
    # Budget is 100000. Usage 99990. Current Request tokens = 20 -> 100010
    status = await mock_circuit_breaker.check(action, 20, 0.5)
    assert status == "HALT"
