import json
import time
from packages.infrastructure.redis_client import UltronRedis

class CoreMemory:
    def __init__(self, redis: UltronRedis):
        self.redis = redis
        self.key = "core_memory:ghost"

    async def get_all(self) -> str:
        data = await self.redis.get(self.key)
        if not data:
            return self.format_for_prompt({
                "ghost_profile": "",
                "current_project": "",
                "today_focus": "",
                "recent_decisions": [],
                "error_patterns": []
            })
        return self.format_for_prompt(json.loads(data))

    async def self_edit(self, field: str, new_value: str, reason: str) -> bool:
        data = await self.redis.get(self.key)
        memory = json.loads(data) if data else {
            "ghost_profile": "",
            "current_project": "",
            "today_focus": "",
            "recent_decisions": [],
            "error_patterns": []
        }
        
        memory[field] = new_value
        
        # Token count check heuristic
        text_content = json.dumps(memory)
        token_estimate = len(text_content.split()) * 1.3
        
        if token_estimate > 500:
            if memory.get("error_patterns"):
                memory["error_patterns"] = []
            elif memory.get("recent_decisions"):
                memory["recent_decisions"] = []
            elif memory.get("today_focus"):
                memory["today_focus"] = ""
                
        await self.redis.set(self.key, json.dumps(memory))
        
        # Append edit log to JSONL archive queue
        log_entry = json.dumps({
            "action_type": "core_memory_edit",
            "field": field,
            "reason": reason,
            "timestamp": int(time.time() * 1000)
        })
        await self.redis.lpush("jsonl_write_queue", log_entry)
        return True

    def format_for_prompt(self, memory: dict) -> str:
        return f"""=== CORE CONTEXT ===
Profile: {memory.get('ghost_profile', '')}
Current Project: {memory.get('current_project', '')}
Today's Focus: {memory.get('today_focus', '')}
Recent Decisions: {', '.join(memory.get('recent_decisions', []))}
Error Patterns: {', '.join(memory.get('error_patterns', []))}
===================="""
