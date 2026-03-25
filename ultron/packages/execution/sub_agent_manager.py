import asyncio
from typing import Dict, Any, Coroutine

class SubAgentManager:
    """Manages parallel execution of sub-agents for isolated tasks."""
    
    def __init__(self):
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.results: Dict[str, Any] = {}

    def spawn(self, agent_id: str, coroutine: Coroutine) -> None:
        """Spawns a new sub-agent task."""
        if agent_id in self.active_tasks and not self.active_tasks[agent_id].done():
            raise ValueError(f"Agent {agent_id} is already running.")
            
        task = asyncio.create_task(coroutine, name=agent_id)
        
        # Add callback to store result
        def _on_done(f: asyncio.Future):
            try:
                self.results[agent_id] = f.result()
            except Exception as e:
                self.results[agent_id] = e
                
            if agent_id in self.active_tasks:
                del self.active_tasks[agent_id]
                
        task.add_done_callback(_on_done)
        self.active_tasks[agent_id] = task

    async def wait_for(self, agent_id: str, timeout: int = 300) -> Any:
        """Waits for a specific agent to finish and returns its result."""
        if agent_id in self.results:
            return self.results[agent_id]
            
        if agent_id not in self.active_tasks:
            raise ValueError(f"Agent {agent_id} not found.")
            
        task = self.active_tasks[agent_id]
        
        try:
            result = await asyncio.wait_for(task, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            task.cancel()
            raise TimeoutError(f"Agent {agent_id} timed out after {timeout}s.")

    def cancel_all(self):
        """Cancels all running sub-agents."""
        for task in self.active_tasks.values():
            if not task.done():
                task.cancel()
        self.active_tasks.clear()
