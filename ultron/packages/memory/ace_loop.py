import json
import logging
import time
import uuid
import os
from typing import Optional, Any
from packages.brain.key_rotation.provider_clients import GeminiClient
from packages.infrastructure.zilliz_client import ZillizPool
from packages.memory.insight.embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)

class ACELoop:
    def __init__(self, gemini_client: GeminiClient, zilliz: ZillizPool, embeddings: EmbeddingGenerator):
        self.gemini_client = gemini_client
        self.zilliz = zilliz
        self.embeddings = embeddings

    async def process_completed_task(self, task: Any, result: str, intermediate_steps: list) -> Optional[dict]:
        task_data = str(task)
        
        reflector_prompt = (
            "What went well? What went wrong? What would you do differently?\n"
            f"Task: {task_data}\nResult: {result}\nSteps: {intermediate_steps}"
        )
        try:
            reflection = await self.gemini_client.generate(prompt=reflector_prompt)
        except Exception:
            return None
            
        curator_prompt = (
            "Extract exactly ONE reusable lesson as JSON: {task_pattern, common_mistake, correct_approach, time_saved_minutes}. "
            "If no lesson, return null.\n"
            f"Reflection: {reflection}"
        )
        try:
            lesson_str = await self.gemini_client.generate(prompt=curator_prompt, system_prompt="You are a JSON generator.")
            cleaned = lesson_str.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:-3]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:-3]
                
            if cleaned.lower() == "null" or not cleaned:
                return None
            lesson = json.loads(cleaned)
        except Exception:
            return None
            
        if not isinstance(lesson, dict) or "task_pattern" not in lesson:
            return None
            
        lesson_text = json.dumps(lesson)
        vector = self.embeddings.generate(lesson_text)
        fact_id = str(uuid.uuid4())
        
        record = {
            "id": fact_id,
            "vector": vector,
            "content": lesson_text,
            "fact_type": "lesson",
            "user_id": "ghost",
            "timestamp": int(time.time() * 1000),
            "importance_score": 0.9,
            "access_count": 0,
            "tags": ["lesson_learned"]
        }
        
        await self.zilliz.insert("skill_playbooks", [record])
        
        playbook_dir = "/memory/playbooks"
        if os.path.exists(playbook_dir):
            task_type = lesson.get("task_pattern", "general")
            with open(os.path.join(playbook_dir, f"{task_type}.md"), "a") as f:
                f.write(f"- {lesson_text}\n")
                
        return lesson

    async def get_playbook(self, task_type: str, top_k: int = 5) -> list[dict]:
        vector = self.embeddings.generate(task_type)
        results = await self.zilliz.search("skill_playbooks", vector, top_k=top_k)
        return results
