import json
import logging
import os
from typing import Literal
from packages.infrastructure.redis_client import UltronRedis
from packages.interface.discord_sender import DiscordSender

logger = logging.getLogger(__name__)

class TokenBudgetGuardian:
    def __init__(self, agent_id: str, redis: UltronRedis, discord_sender: DiscordSender):
        self.agent_id = agent_id
        self.redis = redis
        self.discord_sender = discord_sender
        
        permissions_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "config", "permissions.json"
        )
        with open(permissions_path, "r") as f:
            permissions = json.load(f)
            self.budgets = permissions.get("token_budgets", {})

    async def check(self, tokens_used: int, task_type: str) -> Literal["OK", "WARNING", "HALT"]:
        budget = self.budgets.get(task_type, self.budgets.get("simple_task", 10000))
        
        current_usage_bytes = await self.redis.hget(f"token_budget:{self.agent_id}", "tokens_used")
        current_usage = int(current_usage_bytes) if current_usage_bytes else 0
        
        projected_usage = current_usage + tokens_used
        ratio = projected_usage / budget if budget > 0 else 1.0
        
        if ratio >= 1.0:
            return "HALT"
        elif ratio >= 0.8:
            logger.warning(f"Agent {self.agent_id} approaching budget limit for {task_type}")
            await self.discord_sender.send_message(f"⚠️ Agent {self.agent_id} at {ratio*100:.1f}% of token budget for {task_type}")
            return "WARNING"
        return "OK"

    async def consume(self, tokens: int, agent_id: str) -> None:
        await self.redis.hincrby(f"token_budget:{agent_id}", "tokens_used", tokens)
        await self.redis.hincrby("token_budget:daily", "tokens_used", tokens)
