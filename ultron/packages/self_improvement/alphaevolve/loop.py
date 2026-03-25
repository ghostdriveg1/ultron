import asyncio
from typing import List, Dict

from .whitelist_enforcer import WhitelistEnforcer
from .diff_generator import DiffGenerator
from .pr_creator import PRCreator
from .tests_validator import TestsValidator
from packages.infrastructure.redis_client import UltronRedis

class AlphaEvolveLoop:
    """Background engine that continuously finds and proposes improvement PRs."""
    
    def __init__(self, redis: UltronRedis, git_tool, tester_tool):
        self.enforcer = WhitelistEnforcer()
        self.differ = DiffGenerator()
        self.pr_creator = PRCreator(git_tool)
        self.validator = TestsValidator(tester_tool)
        self.redis = redis
        self._task = None

    async def start(self):
        if self._task is None:
            self._task = asyncio.create_task(self._evolution_loop())

    async def _evolution_loop(self):
        while True:
            # 1. Fetch weak prompts or inefficient code metrics from Redis
            # (e.g. from the Dispatcher's entropy ratings)
            
            # 2. Use Gemini to propose a rewrite (Mocking here)
            proposed_changes = [] # List of (filepath, old_content, new_content)
            
            # 3. Apply changes and validate
            for filepath, old_c, new_c in proposed_changes:
                if not self.enforcer.is_allowed(filepath):
                    continue
                    
                diff = self.differ.generate_diff(old_c, new_c, filepath)
                
                # 4. Run tests
                passed = await self.validator.validate(diff)
                
                # 5. Create PR if tests pass
                if passed:
                    await self.pr_creator.create_pr(
                        diff, 
                        "Automated Self-Improvement PR", 
                        f"AlphaEvolve: Optimization for {filepath}"
                    )
            
            # Sleep for an hour before next evolution cycle
            await asyncio.sleep(3600)

    def stop(self):
        if self._task and not self._task.done():
            self._task.cancel()
