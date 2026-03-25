import json
from packages.infrastructure.redis_client import UltronRedis

class SkillBuilder:
    """Extracts repeated execution patterns and stores them as distinct 'Skills'."""
    
    def __init__(self, redis: UltronRedis):
        self.redis = redis

    async def extract_skill(self, task_history: list, skill_name: str, desc: str):
        """Builds a declarative skill workflow from successful task traces."""
        # Simple extraction mock
        steps = []
        for action in task_history:
            if action.get("success"):
                steps.append({
                    "tool": action.get("tool"),
                    "params": action.get("params")
                })
                
        skill_doc = {
            "name": skill_name,
            "description": desc,
            "workflow": steps
        }
        
        await self.redis.set(f"skill:{skill_name}", json.dumps(skill_doc))
        return True
