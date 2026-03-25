import asyncio
import hashlib
import json
import time
from typing import Dict, Any, Optional

from pydantic import BaseModel, ValidationError

from .registry import ToolRegistry
from .permissions import PermissionChecker
from packages.infrastructure.redis_client import UltronRedis
from packages.interface.discord_sender import DiscordSender

class PermissionDeniedError(Exception):
    pass

class ToolDispatcher:
    """Dispatches tool execution with validation, permissions, and logging."""

    def __init__(self, registry: ToolRegistry, permission_checker: PermissionChecker, 
                 redis: UltronRedis, discord: DiscordSender):
        self.registry = registry
        self.permission_checker = permission_checker
        self.redis = redis
        self.discord = discord
        self.log_file = "logs/tools.jsonl"

    async def dispatch(self, tool_name: str, params: Dict[str, Any], entropy_score: float = 0.0) -> BaseModel:
        start_time = time.time()
        tool = self.registry.get(tool_name)

        try:
            validated_params = tool.input_schema.model_validate(params)
        except ValidationError as e:
            # Re-raise directly to preserve error context
            raise e

        perm_action = self.permission_checker.check(tool_name, tool.permission_level, entropy_score)
        
        if perm_action == "DENY":
            raise PermissionDeniedError(f"Execution of '{tool_name}' denied (Entropy: {entropy_score})")
        elif perm_action == "CONFIRM" or tool.requires_ghost_confirm:
            confirmed = await self._request_ghost_confirmation(tool_name, params)
            if not confirmed:
                raise PermissionDeniedError(f"Ghost confirmation denied or timed out for '{tool_name}'")

        success = True
        result = None
        try:
            raw_result = await tool.execute(validated_params)
            
            # Validate output payload against tool's output schema
            if hasattr(raw_result, "model_dump"):
                result = tool.output_schema.model_validate(raw_result.model_dump())
            elif isinstance(raw_result, dict):
                result = tool.output_schema.model_validate(raw_result)
            else:
                result = tool.output_schema.model_validate(raw_result)
                
            return result
        except Exception:
            success = False
            raise
        finally:
            duration_ms = int((time.time() - start_time) * 1000)
            params_hash = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()
            
            result_hash = None
            if success and result is not None:
                result_hash = hashlib.sha256(result.model_dump_json().encode()).hexdigest()
            
            self._log_execution(tool_name, params_hash, result_hash, duration_ms, success)

    async def _request_ghost_confirmation(self, tool_name: str, params: Dict[str, Any]) -> bool:
        params_hash = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()
        confirm_key = f"ghost_confirm:{tool_name}:{params_hash}"
        
        msg = f"**CONFIRMATION REQUIRED**\nTool: `{tool_name}`\nParams: ```json\n{json.dumps(params, indent=2)}\n```"
        await self.discord.send_message(msg)

        for _ in range(60): # 60 * 5s = 5 minutes
            val = await self.redis.get(confirm_key)
            if val == "1" or val == b"1":
                return True
            elif val == "0" or val == b"0":
                return False
            await asyncio.sleep(5)
            
        return False

    def _log_execution(self, tool_name: str, params_hash: str, result_hash: Optional[str], duration_ms: int, success: bool):
        log_entry = {
            "tool_name": tool_name,
            "params_hash": params_hash,
            "result_hash": result_hash,
            "duration_ms": duration_ms,
            "success": success,
            "timestamp": time.time()
        }
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except FileNotFoundError:
            pass # Ignore if logs directory doesn't exist yet
