import json
import asyncio
from pydantic import BaseModel
from packages.memory.core_memory import CoreMemory
from packages.memory.working_memory import WorkingMemory
from packages.memory.retrieval_engine import RetrievalEngine
from packages.memory.ace_loop import ACELoop

class Passport(BaseModel):
    content: str
    token_count: int
    sources_used: list[str]

class PassportAssembler:
    def __init__(self, core: CoreMemory, working: WorkingMemory, retrieval: RetrievalEngine, ace: ACELoop):
        self.core = core
        self.working = working
        self.retrieval = retrieval
        self.ace = ace

    async def assemble(self, task_id: str, task_description: str) -> Passport:
        sources = []
        token_count = 0
        
        async def _get_core(): return await self.core.get_all()
        async def _get_working(): return await self.working.get_current(task_id)
        async def _get_retrieval(): return await self.retrieval.search(task_description, top_k=10)
        async def _get_cognee(): return self.retrieval.cognee.traverse(task_description, max_depth=2)
        async def _get_ace(): return await self.ace.get_playbook(task_description, top_k=5)

        results = await asyncio.gather(
            _get_core(),
            _get_working(),
            _get_retrieval(),
            _get_cognee(),
            _get_ace(),
            return_exceptions=True
        )

        core_text = results[0] if not isinstance(results[0], Exception) else ""
        working_text = results[1] if not isinstance(results[1], Exception) else ""
        retrieval_res = results[2] if not isinstance(results[2], Exception) else []
        cognee_res = results[3] if not isinstance(results[3], Exception) else []
        ace_res = results[4] if not isinstance(results[4], Exception) else []

        def _truncate(text: str, max_tokens: int) -> str:
            words = text.split()
            max_words = int(max_tokens / 1.3)
            return " ".join(words[:max_words])

        sections = [
            ("core_memory", core_text)
        ]
        
        if working_text:
            sections.append(("working_memory", f"=== WORKING MEMORY ===\n{_truncate(working_text, 150)}"))
            
        retrieval_text = json.dumps(retrieval_res) if retrieval_res else ""
        if retrieval_text:
            sections.append(("retrieval_engine", f"=== RELEVANT CONTEXT ===\n{_truncate(retrieval_text, 250)}"))
            
        cognee_text = json.dumps(cognee_res) if cognee_res else ""
        if cognee_text:
            sections.append(("cognee", f"=== KNOWLEDGE GRAPH ===\n{_truncate(cognee_text, 100)}"))
            
        ace_text = json.dumps(ace_res) if ace_res else ""
        if ace_text:
            sections.append(("ace_playbook", f"=== ACE PLAYBOOK ===\n{_truncate(ace_text, 100)}"))

        def _get_tokens(sections_list):
            content = "\n\n".join(text for _, text in sections_list)
            return int(len(content.split()) * 1.3), content

        token_count, final_content = _get_tokens(sections)

        drop_order = ["ace_playbook", "cognee", "retrieval_engine", "working_memory"]
        for section_to_drop in drop_order:
            if token_count <= 800:
                break
            sections = [s for s in sections if s[0] != section_to_drop]
            token_count, final_content = _get_tokens(sections)

        sources = [name for name, _ in sections]
        passport = Passport(content=final_content, token_count=token_count, sources_used=sources)
        await self.core.redis.set(f"passport:{task_id}", passport.model_dump_json(), ex=3600)
            
        return passport
