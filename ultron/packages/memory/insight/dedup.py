import math
from packages.infrastructure.zilliz_client import ZillizPool
from packages.memory.insight.embeddings import EmbeddingGenerator

class DuplicateDetector:
    def __init__(self, zilliz: ZillizPool, embeddings: EmbeddingGenerator):
        self.zilliz = zilliz
        self.embeddings = embeddings

    def cosine_similarity(self, a: list[float], b: list[float]) -> float:
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    async def is_duplicate(self, text: str, collection: str, threshold: float = 0.95) -> bool:
        vector = self.embeddings.generate(text)
        results = await self.zilliz.search(collection, vector, filter_expr="", top_k=1)
        if not results:
            return False
            
        top_result = results[0]
        score = top_result.get("distance", 0.0)
        return score >= threshold
