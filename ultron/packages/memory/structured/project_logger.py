import json
import time
from typing import Any
from packages.memory.structured.notion_client import NotionClient
from packages.memory.jsonl_archive import JSONLArchive

class ProjectLogger:
    def __init__(self, notion: NotionClient, archive: JSONLArchive):
        self.notion = notion
        self.archive = archive

    async def log_decision(self, decision: str, rationale: str, affected_files: list[str]) -> None:
        content = f"Decision: {decision}\nRationale: {rationale}\nAffected Files: {', '.join(affected_files)}"
        
        parent_id = "default_parent_id"
        self.notion.create_page(parent_id, "Architectural Decision", content)
        
        await self.archive.append_event({
            "action_type": "architectural_decision",
            "content": content,
            "timestamp": int(time.time() * 1000)
        })

    async def log_task_completion(self, task: Any, result: str, duration_ms: int) -> None:
        content = f"Task: {task}\nResult: {result}\nDuration: {duration_ms}ms"
        
        await self.archive.append_event({
            "action_type": "task_completion",
            "content": content,
            "duration_ms": duration_ms,
            "task_id": str(getattr(task, 'id', 'unknown')),
            "timestamp": int(time.time() * 1000)
        })
