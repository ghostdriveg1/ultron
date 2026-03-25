import os
import json
import time
import logging
from typing import Any
import httpx
from packages.infrastructure.redis_client import UltronRedis

logger = logging.getLogger(__name__)

class JSONLArchive:
    def __init__(self, redis: UltronRedis):
        self.redis = redis
        self.github_token = os.getenv("GITHUB_TOKEN")
        
    async def append_event(self, event: dict) -> None:
        line = {
            "event_id": event.get("event_id", ""),
            "trace_id": event.get("trace_id", ""),
            "timestamp": event.get("timestamp", int(time.time() * 1000)),
            "action_type": event.get("action_type", ""),
            "agent_id": event.get("agent_id", "ghost"),
            "task_id": event.get("task_id", ""),
            "input_hash": event.get("input_hash", ""),
            "output_hash": event.get("output_hash", ""),
            "model_used": event.get("model_used", ""),
            "tokens_used": event.get("tokens_used", 0),
            "duration_ms": event.get("duration_ms", 0),
            "success": event.get("success", True),
            "entropy_score_before": event.get("entropy_score_before", 0.0),
            "entropy_score_after": event.get("entropy_score_after", 0.0),
            "content": event.get("content", "")
        }
        json_line = json.dumps(line)
        await self.redis.lpush("jsonl_write_queue", json_line)

    async def flush_to_github(self) -> int:
        if not self.github_token:
            logger.error("No GITHUB_TOKEN set for memory archive")
            return 0
            
        queue_len = await self.redis.llen("jsonl_write_queue")
        if queue_len == 0:
            return 0
            
        lines = await self.redis.lrange("jsonl_write_queue", 0, -1)
        decoded_lines = lines
        file_content = "\n".join(decoded_lines) + "\n"
        
        count = len(decoded_lines)
        
        date_str = time.strftime("%Y-%m-%d")
        success_events = await self._append_to_github_file(file_content, "memory/events.jsonl")
        success_daily = await self._append_to_github_file(file_content, f"memory/daily/{date_str}.jsonl")
        
        if success_events and success_daily:
            await self.redis.delete("jsonl_write_queue")
            return count
        return 0

    async def _append_to_github_file(self, content_str: str, file_path: str) -> bool:
        import base64
        repo = os.getenv("GITHUB_REPOSITORY")
        if not repo:
            logger.error("No GITHUB_REPOSITORY set")
            return False
            
        url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            sha = None
            current_content = ""
            if resp.status_code == 200:
                data = resp.json()
                sha = data.get("sha")
                current_content = base64.b64decode(data.get("content", "")).decode("utf-8")
                
            new_content = current_content + content_str
            encoded_content = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")
            
            payload = {
                "message": f"Archive memory to {file_path}",
                "content": encoded_content
            }
            if sha:
                payload["sha"] = sha
                
            put_resp = await client.put(url, headers=headers, json=payload)
            if put_resp.status_code in (200, 201):
                return True
            logger.error(f"GitHub PUT failed: {put_resp.text}")
            return False
