import os
import json
import logging
from packages.brain.key_rotation.provider_clients import GeminiClient

logger = logging.getLogger(__name__)

class RaptorIndex:
    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client
        self.index_path = os.getenv("RAPTOR_INDEX_PATH", "/data/raptor/")
        self._available = True
        
        if not os.path.exists(self.index_path):
            try:
                os.makedirs(self.index_path, exist_ok=True)
            except OSError:
                logger.critical(f"Failed to create RAPTOR volume at {self.index_path}")
                self._available = False
                
        self.files = {
            0: os.path.join(self.index_path, "level_0.jsonl"),
            1: os.path.join(self.index_path, "level_1.jsonl"),
            2: os.path.join(self.index_path, "level_2.jsonl"),
            3: os.path.join(self.index_path, "level_3.jsonl")
        }

    async def add_event(self, event: dict) -> None:
        if not self._available:
            return
            
        with open(self.files[0], "a") as f:
            f.write(json.dumps(event) + "\n")
            
        with open(self.files[0], "r") as f:
            count = sum(1 for _ in f)
            
        if count > 0 and count % 50 == 0:
            await self.compress_level(0)

    async def query(self, question: str) -> str:
        if not self._available:
            return ""
        prompt = (
            f"Question: {question}\n"
            "Which level? 0=individual events, 1=weekly, 2=phase, 3=project. Return ONLY the number."
        )
        try:
            level_str = await self.gemini_client.generate(prompt=prompt)
            level = int(level_str.strip())
        except Exception:
            level = 0
            
        level = max(0, min(3, level))
        file_path = self.files[level]
        if not os.path.exists(file_path):
            return ""
            
        results = []
        with open(file_path, "r") as f:
            # Simple keyword extraction for matching logic as fallback
            first_word = question.lower().split()[0] if question else ""
            for line in f:
                if first_word in line.lower() or not first_word:
                    results.append(line)
        return "\n".join(results[:5])

    async def compress_level(self, level: int) -> None:
        if level >= 3 or not self._available:
            return
            
        file_path = self.files[level]
        if not os.path.exists(file_path):
            return
            
        with open(file_path, "r") as f:
            entries = [json.loads(line) for line in f]
            
        for i in range(0, len(entries), 50):
            batch = entries[i:i+50]
            context = json.dumps(batch)
            prompt = f"Summarize these events concisely:\n{context}"
            try:
                summary = await self.gemini_client.generate(prompt=prompt)
                with open(self.files[level + 1], "a") as next_f:
                    next_f.write(json.dumps({"summary": summary, "source_level": level}) + "\n")
            except Exception as e:
                logger.error(f"Compression failed at level {level}: {e}")
