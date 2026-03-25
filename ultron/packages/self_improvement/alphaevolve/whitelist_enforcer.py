import os

class WhitelistEnforcer:
    """Ensures self-evolution changes only affect allowed prompt strings."""
    
    ALLOWED_FILES = [
        "packages/tools/",
        "packages/prompts/task_specific/",
        "config/model_routing.json",
        "packages/skills/generated/",
        "packages/brain/proposers/prompts/",
        "packages/brain/spec_engine/prompts/",
    ]
    
    FORBIDDEN_FILES = [
        "packages/memory/restore.py",
        "packages/infrastructure/redis_client.py",
        "packages/brain/key_rotation/pool.py",
        "packages/execution/watchdog.py",
        "packages/circuit_breaker/breaker.py",
        "packages/brain/moa/roles.py",
        "packages/self_improvement/alphaevolve/whitelist_enforcer.py",
        "packages/self_improvement/alphaevolve/loop.py",
    ]
    
    def is_allowed(self, filepath: str) -> bool:
        norm_path = os.path.normpath(filepath).replace('\\', '/')
        
        # Check against forbidden
        for forbidden in self.FORBIDDEN_FILES:
            if norm_path == forbidden or norm_path.startswith(forbidden):
                return False
                
        # Must match allowed
        for allowed in self.ALLOWED_FILES:
            if norm_path == allowed or norm_path.startswith(allowed):
                return True
                
        return False
