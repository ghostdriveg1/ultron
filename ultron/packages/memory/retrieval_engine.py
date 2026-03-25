import asyncio
from typing import List, Dict

from packages.memory.insight.mem0_client import Mem0Client
from packages.memory.insight.zilliz_client import MemoryZillizClient
from packages.memory.insight.cognee_client import CogneeClient
from packages.memory.insight.raptor import RaptorIndex
from packages.memory.ace_loop import ACELoop

class RetrievalEngine:
    def __init__(self, mem0: Mem0Client, zilliz_client: MemoryZillizClient, cognee: CogneeClient, raptor: RaptorIndex, ace: ACELoop):
        self.mem0 = mem0
        self.zilliz_client = zilliz_client
        self.cognee = cognee
        self.raptor = raptor
        self.ace = ace

    async def search(self, query: str, top_k: int = 10, filters: dict = None) -> list[dict]:
        async def wrap(coro, source_name):
            try:
                res = await coro
                if isinstance(res, str):
                    return [{"content": res, "source": source_name, "score": 1.0}] if res else []
                out = []
                for item in (res or []):
                    if isinstance(item, dict):
                        item["source"] = source_name
                        out.append(item)
                    elif hasattr(item, "model_dump"):
                        d = item.model_dump()
                        d["source"] = source_name
                        out.append(d)
                    else:
                        out.append({"content": str(item), "source": source_name, "score": 1.0})
                return out
            except Exception:
                return []

        tasks = [
            wrap(self.mem0.search(query, n_results=top_k, filters=filters), "mem0"),
            wrap(self.raptor.query(query), "raptor"),
            wrap(self.ace.get_playbook(query, top_k=3), "ace_playbook")
        ]
        
        results = await asyncio.gather(*tasks)
        
        flattened = [item for sublist in results for item in sublist]
        
        seen = set()
        unique_results = []
        for r in flattened:
            content_hash = hash(r.get("content", ""))
            if content_hash not in seen:
                seen.add(content_hash)
                unique_results.append(r)
                
        unique_results.sort(key=lambda x: x.get("score", x.get("distance", 0.0)), reverse=True)
        return unique_results[:top_k]
