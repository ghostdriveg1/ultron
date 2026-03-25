import json
import asyncio
import time
from typing import Literal, Optional
from pydantic import BaseModel

from packages.infrastructure.redis_client import UltronRedis
from packages.brain.puter_opus_caller import PuterOpusCaller
from packages.interface.discord_sender import DiscordSender
from packages.interface.escalation import send_ghost_alert

from packages.circuit_breaker.semantic_hash import SemanticHashRing
from packages.circuit_breaker.entropy_detector import ProgressEntropyDetector
from packages.circuit_breaker.state_diff import StateDiffMonitor
from packages.circuit_breaker.budget_guardian import TokenBudgetGuardian

class BreakerState(BaseModel):
    state: Literal["CLOSED", "OPEN", "HALF_OPEN"]
    trip_count: int
    last_trip: Optional[str] = None
    open_until: Optional[str] = None
    checkpoint: dict = {}

class CircuitBreaker:
    def __init__(self, agent_id: str, redis: UltronRedis, opus_caller: PuterOpusCaller, discord_sender: DiscordSender):
        self.agent_id = agent_id
        self.redis = redis
        self.opus_caller = opus_caller
        self.discord_sender = discord_sender
        self.state_key = f"circuit_breaker:{agent_id}"

        self.semantic_ring = SemanticHashRing(agent_id, redis)
        self.entropy_detector = ProgressEntropyDetector(agent_id, redis)
        self.state_diff_monitor = StateDiffMonitor(agent_id, redis)
        self.budget_guardian = TokenBudgetGuardian(agent_id, redis, discord_sender)

    async def check(self, action: dict, tokens_used: int, progress: float) -> Literal["PROCEED", "HALT", "ESCALATE"]:
        state_data = await self.redis.get(self.state_key)
        if state_data:
            state = BreakerState.model_validate_json(state_data)
        else:
            state = BreakerState(state="CLOSED", trip_count=0)

        now_ms = int(time.time() * 1000)

        if state.state == "OPEN":
            if not state.open_until or int(state.open_until) > now_ms:
                return "HALT"
            # transition to HALF_OPEN
            state.state = "HALF_OPEN"
            await self.redis.set(self.state_key, state.model_dump_json())

        # budget check
        task_type = action.get("target_type", "simple_task")
        budget_status = await self.budget_guardian.check(tokens_used, task_type)
        if budget_status == "HALT":
            return "HALT"

        # run detectors
        async def wrap(fn, *args):
            res = fn(*args)
            if asyncio.iscoroutine(res):
                return await res
            return res

        results = await asyncio.gather(
            wrap(self.semantic_ring.is_loop, action),
            wrap(self.entropy_detector.is_loop, tokens_used, progress),
            wrap(self.state_diff_monitor.is_loop)
        )

        triggered = any(results)
        if triggered:
            detectors = ["SemanticHash", "ProgressEntropy", "StateDiff"]
            triggered_names = [detectors[i] for i, r in enumerate(results) if r]
            return await self._handle_trip(triggered_names, action, state, now_ms)
        
        return "PROCEED"

    async def _handle_trip(self, triggered_detectors: list[str], action: dict, state: BreakerState, now_ms: int) -> Literal["HALT", "ESCALATE", "PROCEED"]:
        checkpoint = {"action": action, "detectors": triggered_detectors}
        await self.redis.set(f"{self.state_key}:checkpoint", json.dumps(checkpoint))
        
        meta_key = f"{self.state_key}:meta"
        await self.redis.hincrby(meta_key, "trip_count", 1)
        
        trip_count_str = await self.redis.hget(meta_key, "trip_count")
        trip_count = int(trip_count_str) if trip_count_str else state.trip_count + 1

        state.trip_count = trip_count
        state.state = "OPEN"
        state.open_until = str(now_ms + 10 * 60 * 1000) # 10 minutes
        state.last_trip = str(now_ms)
        state.checkpoint = checkpoint
        
        await self.redis.set(self.state_key, state.model_dump_json())

        if trip_count <= 2:
            await self.redis.delete(f"action_ring:{self.agent_id}")
            # auto-recovery
            await self.opus_caller.call({"role": "system", "content": f"Loop detected: {triggered_detectors}. Suggest new approach."})
            # inject new approach into task_queue sorted set (mocked logic or direct redis usage based on exact implementation)
            state.state = "HALF_OPEN"
            await self.redis.set(self.state_key, state.model_dump_json())
            return "HALT" # Wait for next turn
        else:
            await send_ghost_alert(
                "circuit_breaker", 
                f"Agent {self.agent_id} in {triggered_detectors} loop", 
                ["RETRY", "SKIP", "ABORT"]
            )
            state.state = "OPEN"
            state.open_until = None
            await self.redis.set(self.state_key, state.model_dump_json())
            return "ESCALATE"
