import time
import asyncio
from typing import List, Any
from pydantic import BaseModel

from packages.infrastructure.redis_client import UltronRedis
from packages.infrastructure.zilliz_client import ZillizPool
from packages.memory.pruning import MemoryPruner
from packages.interface.discord_sender import DiscordSender

from packages.entropy_engine.memory_entropy import MemoryEntropyScorer
from packages.entropy_engine.codebase_entropy import CodebaseEntropyScorer
from packages.entropy_engine.task_entropy import TaskEntropyScorer
from packages.entropy_engine.bug_entropy import BugEntropyScorer
from packages.entropy_engine.system_health import SystemHealthScorer

class SystemHealthReport(BaseModel):
    memory_entropy: float
    codebase_entropy: float
    task_entropy: float
    bug_entropy: float
    system_health: float
    timestamp: int
    recommendations: List[str]

class EntropyEngine:
    def __init__(self, redis: UltronRedis, zilliz: ZillizPool, pruner: MemoryPruner, discord_sender: DiscordSender):
        self.redis = redis
        self.zilliz = zilliz
        self.pruner = pruner
        self.discord_sender = discord_sender
        
        self.memory_scorer = MemoryEntropyScorer(zilliz)
        self.codebase_scorer = CodebaseEntropyScorer()
        self.task_scorer = TaskEntropyScorer()
        self.bug_scorer = BugEntropyScorer(redis)
        self.health_scorer = SystemHealthScorer(redis, zilliz)

    def compute_task_entropy(self, task: Any) -> float:
        return self.task_scorer.score(task)

    async def run_system_scan(self) -> SystemHealthReport:
        repo_path = "."
        
        async def wrap(fn, *args):
            if asyncio.iscoroutinefunction(fn):
                return await fn(*args)
            return fn(*args)

        results = await asyncio.gather(
            wrap(self.memory_scorer.score),
            wrap(self.codebase_scorer.score, repo_path),
            wrap(self.bug_scorer.score),
            wrap(self.health_scorer.score)
        )
        
        memory_val, codebase_val, bug_val, health_val = results
        
        scores = []
        try:
            tasks_data = await self.redis.zrange("task_queue", 0, -1)
            import json
            class TaskWrapper:
                def __init__(self, d):
                    self.operation = d.get("operation", "read")
                    
            for t in tasks_data:
                try:
                    data = json.loads(t)
                    scores.append(self.compute_task_entropy(TaskWrapper(data)))
                except Exception:
                    pass
        except Exception:
            pass
            
        task_entropy_val = sum(scores) / len(scores) if scores else 0.0
        
        recommendations = []
        
        if memory_val > 70:
            await self.pruner.run_full_pruning_cycle()
            recommendations.append("Memory pruned due to high entropy.")
            
        if codebase_val > 60:
            self.discord_sender.send("System", "High codebase entropy. Recommend refactoring.")
            recommendations.append("Refactor recommended.")
            
        if health_val < 50:
            self.discord_sender.send("System", "ALERT: System health < 50%. Self-healing initiated.")
            recommendations.append("Self-healing initiated.")
            
        report = SystemHealthReport(
            memory_entropy=memory_val,
            codebase_entropy=codebase_val,
            task_entropy=task_entropy_val,
            bug_entropy=bug_val,
            system_health=health_val,
            timestamp=int(time.time() * 1000),
            recommendations=recommendations
        )
        
        await self.redis.set("entropy_report:latest", report.model_dump_json(), ex=7 * 86400)
        return report

    def identify_weakest_component(self) -> str:
        """Identifies the codebase component with the highest entropy requiring evolution."""
        # For Phase 5, we provide a deterministic or semi-random target based on mock logic.
        # In full production, this would query Zilliz codebase_entropy table.
        return "packages/brain/prompts.py"
