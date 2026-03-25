import asyncio
from pydantic import BaseModel
from typing import Optional

from .xvfb_manager import XvfbManager
from .vision import GeminiVisionAnalyzer
from .ui_tars import UITARSGrounder
from .action_executor import ActionExecutor
from packages.infrastructure.redis_client import UltronRedis
from packages.interface.discord_sender import DiscordSender
from packages.brain.lats import LATS
from packages.execution.entropy_scheduler import Task

class ParsedAction(BaseModel):
    action_type: str
    text_to_type: Optional[str] = None
    url: Optional[str] = None
    scroll_amount: Optional[int] = 500

class ComputerUseResult(BaseModel):
    success: bool
    iterations_used: int
    final_screenshot_base64: str

class ComputerUseController:
    """Orchestrates the computer use flow using LATS planning."""
    
    def __init__(self, xvfb: XvfbManager, vision: GeminiVisionAnalyzer, 
                 grounder: UITARSGrounder, executor: ActionExecutor,
                 redis: UltronRedis, discord: DiscordSender):
        self.xvfb = xvfb
        self.vision = vision
        self.grounder = grounder
        self.executor = executor
        self.redis = redis
        self.discord = discord
        self.lats = LATS()

    async def execute_task(self, task_description: str, max_iterations: int = 50) -> ComputerUseResult:
        await self.xvfb.start()
        
        iterations = 0
        success = False
        final_ss = ""
        
        try:
            for i in range(max_iterations):
                iterations += 1
                
                # 1. Perceive screen state via Vision
                screenshot = await self.executor.screenshot()
                final_ss = screenshot
                screen_state = await self.vision.understand_screen(screenshot)
                
                # Gemini Vision completion_check(screen_state,task)
                is_complete = await self.vision.completion_check(screen_state, task_description)
                if is_complete:
                    success = True
                    break
                    
                # 2. Plan using LATS with visual context
                task_obj = Task(id=f"step_{i}", description=f"Goal: {task_description}\nCurrent State: {screen_state}", entropy=0.5, type="COMPUTER_USE")
                plan = await self.lats.plan(task=task_obj, n_simulations=3)
                next_step = plan.steps[0] if plan.steps else "evaluate screen"
                
                # 3. Ground via real UI-TARS
                coords = await self.grounder.ground_element(screenshot, next_step)
                
                # 4. Action Variety based on LATS string output
                step_lower = next_step.lower()
                action_data = {"action_type": "click"}
                if "type" in step_lower:
                    action_data["action_type"] = "type"
                    text_parts = next_step.split("'", 2)
                    action_data["text_to_type"] = text_parts[1] if len(text_parts) > 1 else "default"
                elif "scroll" in step_lower:
                    action_data["action_type"] = "scroll"
                elif "nav" in step_lower or "goto" in step_lower:
                    action_data["action_type"] = "navigate"
                    url_parts = next_step.split(" ")
                    action_data["url"] = url_parts[-1] if "http" in url_parts[-1] else "https://google.com"
                    
                parsed_action = ParsedAction(**action_data)
                
                if not coords or len(coords) < 2:
                    coords = (0, 0)
                    
                if parsed_action.action_type == "type":
                    await self.executor.click(coords[0], coords[1])
                    if hasattr(self.executor, 'type_text') and parsed_action.text_to_type:
                        await self.executor.type_text(parsed_action.text_to_type)
                elif parsed_action.action_type == "scroll":
                    if hasattr(self.executor, 'scroll'):
                        await self.executor.scroll(0, parsed_action.scroll_amount)
                elif parsed_action.action_type == "navigate":
                    if hasattr(self.executor, 'navigate') and parsed_action.url:
                        await self.executor.navigate(parsed_action.url)
                else:
                    await self.executor.click(coords[0], coords[1])
                    
            if iterations >= max_iterations and not success:
                alert_msg = f"Escalation: Computer Use task timed out after {max_iterations} iterations.\nTask: {task_description}"
                # max_iter Discord+screenshot
                if hasattr(self.discord, 'send_message'):
                    await self.discord.send_message(alert_msg, image=final_ss)
                elif hasattr(self.discord, 'send'):
                    self.discord.send("UltronAlerts", alert_msg, image=final_ss)
                
        finally:
            await self.executor.close()
            await self.xvfb.stop()
            
        return ComputerUseResult(
            success=success,
            iterations_used=iterations,
            final_screenshot_base64=final_ss
        )
