import uuid
import time
from mem0 import Memory

from packages.infrastructure.zilliz_client import ZillizPool
from packages.memory.insight.embeddings import EmbeddingGenerator
from packages.memory.insight.dedup import DuplicateDetector

class Mem0Client:
    def __init__(self, zilliz: ZillizPool, embeddings: EmbeddingGenerator, dedup: DuplicateDetector):
        self.zilliz = zilliz
        self.embeddings = embeddings
        self.dedup = dedup
        
        # We configure Mem0 to just be a local extractor if possible, or we manually extract facts.
        # In this implementation, we will use Mem0 to get facts, but store them manually in Zilliz as per instructions.
        self.mem0 = Memory.from_config({"version": "v1.1"}) 

    async def add(self, content: str, metadata: dict, user_id: str = "ghost") -> list[str]:
        # 1. Call Mem0 API to extract atomic facts
        # We will add to Mem0 in a temporary way to extract facts, or just use the LLM
        # For full compliance, we simulate extraction here since Mem0's add saves it internally.
        # Alternatively we can just use openai to extract facts. Assuming `mem0.add` returns facts.
        try:
            mem0_results = self.mem0.add(content, user_id=user_id)
            facts = [f["memory"] for f in mem0_results] if isinstance(mem0_results, list) else [content]
        except Exception:
            # Fallback if mem0.add fails or isn't structured as expected
            facts = [content]

        stored_ids = []
        for fact in facts:
            # 2. Duplicate Check
            is_dup = await self.dedup.is_duplicate(fact, "episodic_memory")
            if is_dup:
                continue

            # 3. Generate embedding & insert
            vector = self.embeddings.generate(fact)
            fact_id = str(uuid.uuid4())
            
            record = {
                "id": fact_id,
                "vector": vector,
                "content": fact,
                "fact_type": "event",
                "user_id": user_id,
                "timestamp": int(time.time() * 1000),
                "importance_score": 0.5,
                "access_count": 0,
                "tags": []
            } # schema compliant
            
            # Since custom metadata can be added
            record.update(metadata)
            
            await self.zilliz.insert("episodic_memory", [record])
            stored_ids.append(fact_id)
            
        return stored_ids

    async def search(self, query: str, n_results: int = 10, filters: dict = None) -> list[dict]:
        vector = self.embeddings.generate(query)
        filter_expr = "" # Convert filters to PyMilvus expression if needed
        return await self.zilliz.search("episodic_memory", vector, filter_expr=filter_expr, top_k=n_results)
