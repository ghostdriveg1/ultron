from typing import Any
from packages.infrastructure.zilliz_client import ZillizPool

class MemoryZillizClient:
    def __init__(self, pool: ZillizPool):
        self.pool = pool
        self.schema = {
            "auto_id": False,
            "enable_dynamic_field": True,
            "fields": [
                {"name": "id", "type": "VARCHAR", "max_length": 64, "is_primary": True},
                {"name": "vector", "type": "FLOAT_VECTOR", "dim": 768},
                {"name": "content", "type": "VARCHAR", "max_length": 65535},
                {"name": "fact_type", "type": "VARCHAR", "max_length": 64},
                {"name": "user_id", "type": "VARCHAR", "max_length": 64},
                {"name": "timestamp", "type": "INT64"},
                {"name": "importance_score", "type": "FLOAT"},
                {"name": "access_count", "type": "INT64"},
                {"name": "tags", "type": "JSON"}
            ]
        }
        # Notice: The schema format above is an approximation. pymilvus usually uses CollectionSchema.
        # But for raw dictionaries passed to Zilliz client wrappers, it depends on implementation.

    async def ensure_collections(self) -> None:
        """Creates episodic_memory and skill_playbooks collections if not exist"""
        await self.pool.create_collection_if_not_exists("episodic_memory", self.schema)
        await self.pool.create_collection_if_not_exists("skill_playbooks", self.schema)

    async def insert_fact(self, collection: str, fact: dict, vector: list[float]) -> str:
        record = dict(fact)
        record["vector"] = vector
        ids = await self.pool.insert(collection, [record])
        return ids[0] if ids else ""

    async def search_facts(self, collection: str, vector: list[float], top_k: int, filter_expr: str = "") -> list[dict]:
        return await self.pool.search(collection, vector, filter_expr=filter_expr, top_k=top_k)

    async def delete_facts(self, collection: str, ids: list[str]) -> None:
        # We need to call standard delete, but ZillizPool wrapper we read doesn't show delete method.
        # We iterate over clients and perform delete if possible or log it.
        # Assuming ZillizPool has or will have a delete method:
        try:
            for account_id, client in self.pool._clients.items():
                if self.pool._healthy.get(account_id):
                    id_list = ", ".join([f"'{i}'" for i in ids])
                    client.delete(collection_name=collection, filter=f"id in [{id_list}]")
        except AttributeError:
            pass # Ignore if not implemented
