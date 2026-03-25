import time
from pydantic import BaseModel
from packages.infrastructure.zilliz_client import ZillizPool
from packages.memory.jsonl_archive import JSONLArchive

class PruningReport(BaseModel):
    deleted_count: int
    archived_count: int
    dedup_count: int
    duration_seconds: float

class MemoryPruner:
    def __init__(self, zilliz: ZillizPool, archive: JSONLArchive):
        self.zilliz = zilliz
        self.archive = archive
        self.protected_tags = {"critical", "architectural_decision", "ghost_preference", "lesson_learned", "recurring_pattern"}

    async def run_full_pruning_cycle(self) -> PruningReport:
        start_time = time.time()
        
        deleted_count = 0
        archived_count = 0
        dedup_count = 0
        
        now_ms = int(time.time() * 1000)
        days_60_ms = 60 * 24 * 60 * 60 * 1000
        days_30_ms = 30 * 24 * 60 * 60 * 1000
        ttl_threshold = now_ms - days_60_ms
        imp_threshold = now_ms - days_30_ms

        for account_id, client in self.zilliz._clients.items():
            if not self.zilliz._healthy.get(account_id):
                continue
                
            try:
                collections = client.list_collections()
                for col in collections:
                    try:
                        res = client.query(collection_name=col, filter="timestamp > 0", output_fields=["*"])
                    except:
                        try:
                            res = client.query(collection_name=col, filter="id >= 0", output_fields=["*"])
                        except:
                            res = []
                            
                    ids_to_delete = []
                    seen_texts = set()
                    
                    for record in res:
                        tags = record.get("tags", [])
                        if isinstance(tags, str):
                            tags = [tags]
                        
                        is_protected = any(pt in tags for pt in self.protected_tags)
                        if is_protected:
                            continue
                            
                        timestamp = record.get("timestamp", now_ms)
                        access_count = record.get("access_count", 0)
                        importance = record.get("importance_score", 1.0)
                        content = record.get("content", record.get("text", ""))
                        
                        should_prune = False
                        is_dedup = False
                        
                        # Policy 1 - Deduplication
                        if content and content in seen_texts:
                            should_prune = True
                            is_dedup = True
                        elif content:
                            seen_texts.add(content)
                            
                        # Policy 2 - TTL
                        if not should_prune and access_count < 3 and timestamp < ttl_threshold:
                            should_prune = True
                            
                        # Policy 3 - Importance
                        if not should_prune and importance < 0.2 and timestamp < imp_threshold:
                            should_prune = True
                            
                        if should_prune:
                            rec_id = record.get("id")
                            if rec_id is not None:
                                ids_to_delete.append(rec_id)
                                await self.archive.append_event({
                                    "action_type": "pruned_memory",
                                    "reason": "dedup" if is_dedup else "ttl_or_importance",
                                    "content": str(record),
                                    "timestamp": now_ms
                                })
                                archived_count += 1
                                if is_dedup:
                                    dedup_count += 1
                                    
                    if ids_to_delete:
                        client.delete(collection_name=col, pks=ids_to_delete)
                        deleted_count += len(ids_to_delete)
            except Exception:
                pass
        
        report = PruningReport(
            deleted_count=deleted_count,
            archived_count=archived_count,
            dedup_count=dedup_count,
            duration_seconds=time.time() - start_time
        )
        return report
