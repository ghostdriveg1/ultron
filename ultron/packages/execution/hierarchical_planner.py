import json
from typing import List, Optional
from pydantic import BaseModel
from packages.infrastructure.redis_client import UltronRedis

class Ticket(BaseModel):
    id: str
    description: str

class Milestone(BaseModel):
    id: str
    description: str

class LocalPlan(BaseModel):
    milestone_id: str
    tickets: List[Ticket]
    current_ticket_idx: int = 0

class GlobalPlan(BaseModel):
    project_id: str
    goal: str
    milestones: List[Milestone]
    current_milestone_idx: int = 0

class HierarchicalPlanner:
    """Breaks down high-level goals into executable plans and tracks progress."""
    
    def __init__(self, redis: UltronRedis):
        self.redis = redis
        # In real impl, would take a GeminiClient for generation

    async def create_global_plan(self, goal: str, deadline: str) -> GlobalPlan:
        # Call Gemini 2.5 Pro to decompose goal...
        # Mocking for Phase 5 template
        milestones = [
            Milestone(id="m1", description="Foundation setup"),
            Milestone(id="m2", description="Core features implementation"),
            Milestone(id="m3", description="Testing and launch")
        ]
        
        project_id = f"proj_{int(time.time() if 'time' in globals() else 1000)}"
        plan = GlobalPlan(project_id=project_id, goal=goal, milestones=milestones)
        
        await self.redis.set(f"project:{project_id}", plan.model_dump_json())
        return plan

    async def create_local_plan(self, milestone: Milestone) -> LocalPlan:
        # Call Gemini to decompose milestone into tickets
        tickets = [
            Ticket(id=f"{milestone.id}_t1", description="Implement part 1"),
            Ticket(id=f"{milestone.id}_t2", description="Implement part 2")
        ]
        return LocalPlan(milestone_id=milestone.id, tickets=tickets)

    async def advance(self, project_id: str) -> Optional[Ticket]:
        """Returns the next unfinished ticket and updates state."""
        plan_str = await self.redis.get(f"project:{project_id}")
        if not plan_str:
            return None
            
        plan_data = json.loads(plan_str)
        plan = GlobalPlan(**plan_data)
        
        # Simplified progression mock
        if plan.current_milestone_idx >= len(plan.milestones):
            return None # Project complete
            
        current_milestone = plan.milestones[plan.current_milestone_idx]
        
        # Load local plan for milestone
        local_plan_str = await self.redis.get(f"local_plan:{current_milestone.id}")
        if not local_plan_str:
            local_plan = await self.create_local_plan(current_milestone)
            await self.redis.set(f"local_plan:{current_milestone.id}", local_plan.model_dump_json())
        else:
            local_plan = LocalPlan(**json.loads(local_plan_str))
            
        if local_plan.current_ticket_idx >= len(local_plan.tickets):
            # Milestone complete, advance to next
            plan.current_milestone_idx += 1
            await self.redis.set(f"project:{project_id}", plan.model_dump_json())
            return await self.advance(project_id) # Recurse
            
        next_ticket = local_plan.tickets[local_plan.current_ticket_idx]
        
        # Mark ticket as started/completed (simplified)
        local_plan.current_ticket_idx += 1
        await self.redis.set(f"local_plan:{current_milestone.id}", local_plan.model_dump_json())
        
        return next_ticket
