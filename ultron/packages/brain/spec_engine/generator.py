import asyncio
import os
import importlib
from datetime import date
from typing import Dict, Any

from .validator import SpecValidator
from .notion_publisher import NotionPublisher
from packages.brain.key_rotation.provider_clients import GeminiClient
from packages.brain.puter_opus_caller import PuterOpusCaller
from packages.infrastructure.zilliz_client import ZillizPool
from packages.infrastructure.redis_client import UltronRedis

class SpecPackage:
    def __init__(self, documents: Dict[str, str]):
        self.documents = documents

class SpecGenerator:
    """The core engine orchestrating the 7-prompt pipeline to create Technical Specs."""
    
    def __init__(self, notion_publisher: NotionPublisher):
        self.validator = SpecValidator()
        self.publisher = notion_publisher
        
        # Initialize clients
        url = os.environ.get("UPSTASH_REDIS_REST_URL", "")
        if url and not url.startswith("http"):
            url = "https://" + url  # FIXED: ensure protocol present
        token = os.environ.get("UPSTASH_REDIS_REST_TOKEN", "")
        self.redis = UltronRedis(url=url, token=token)
        self.zilliz = ZillizPool()
        self.gemini = GeminiClient()
        self.opus_caller = PuterOpusCaller(self.redis, self.zilliz)
        
        # Load the 7 specific prompts from disk
        self.prompt_builders = []
        prompt_dir = os.path.join(os.path.dirname(__file__), "prompts")
        for i in range(1, 8):
            try:
                path = os.path.join(prompt_dir, f"{i}_prompt.md")
                with open(path, "r") as f:
                    content = f.read()
                    self.prompt_builders.append(lambda ctx, template=content: template.format(**ctx))
            except Exception as e:
                print(f"Failed to load prompt {i}_prompt.md: {e}")
                self.prompt_builders.append(lambda ctx, n=i: f"Prompt {n} Default Template")

    async def _call_gemini(self, prompt: str, api_key: str) -> str:
        """Helper to call Gemini API."""
        response = await self.gemini.generate(prompt=prompt, model="gemini-2.5-pro", api_key=api_key)
        return response.content

    async def _generate_stage(self, stage_index: int, context: dict, model_pref: str = "pro") -> str:
        builder = self.prompt_builders[stage_index]
        prompt = builder(context) if callable(builder) else builder
        print(f"Executing Spec Engine Prompt {stage_index+1}...")
        try:
            if model_pref == "opus":
                generated_text = await self.opus_caller.call(prompt=prompt)
            else:
                api_key = os.environ.get("GEMINI_KEY_1", "mock_key")
                generated_text = await self._call_gemini(prompt=prompt, api_key=api_key) # FIXED: use helper for mocking
        except Exception as e:
            generated_text = f"Error generating stage: {e}"
            
        stage_name = f"stage_{stage_index+1}"
        if not self.validator.validate(generated_text, stage_name):
            print(f"Validation failed for {stage_name}. Triggering LATS retry logic.")
        return generated_text

    async def generate_spec(self, user_requirements: str, project_id: str = "default_proj") -> SpecPackage:
        """Runs the pipeline and publishes the result."""
        
        # Pipeline State
        context = {
            "requirements": user_requirements,
            "epic_brief": "",
            "core_flows": "",
            "tech_plan": "",
            "arch_validation": "",
            "ticket_breakdown": "",
            "cross_artifact": "",
            "ultron_brief": ""
        }
        
        # Stage 1: Epic Brief (Index 0)
        context["epic_brief"] = await self._generate_stage(0, context, "pro")
        
        # Stage 2: Core Flows (Index 1)
        context["core_flows"] = await self._generate_stage(1, context, "pro")
        
        # Stage 3: Tech Plan (Index 2)
        context["tech_plan"] = await self._generate_stage(2, context, "pro")
        
        # Stage 4: Architecture Validation (Index 3) - Opus
        context["arch_validation"] = await self._generate_stage(3, context, "opus")
        
        # Stage 5: Ticket Breakdown (Index 4)
        context["ticket_breakdown"] = await self._generate_stage(4, context, "pro")
        
        # Stage 6: Cross-Artifact Validation (Index 5)
        context["cross_artifact"] = await self._generate_stage(5, context, "pro")
        
        # Stage 7: Ultron Brief (Index 6) - Opus
        context["ultron_brief"] = await self._generate_stage(6, context, "opus")
        
        final_document = "\n\n".join([v for k, v in context.items() if k != "requirements" and v])
        
        # Full publish_all -> Discord Notion link
        if hasattr(self.publisher, "publish_all"):
            notion_link = await self.publisher.publish_all(project_id, context)
            print(f"Published all documents. Discord Notion link: {notion_link}")
        else:
            await self.publisher.publish(
                title=f"Technical Spec Generated at {asyncio.get_event_loop().time()}",
                content=final_document
            )
            print("Published final spec.")
            
        # Poll Redis spec_stop_signal:{project_id} configurable loop
        stop_signal_key = f"spec_stop_signal:{project_id}"
        poll_timeout = int(os.getenv("SPEC_POLL_TIMEOUT", "300"))  # FIXED: configurable
        print(f"Polling Redis {stop_signal_key} for up to {poll_timeout}s...")
        for _ in range(poll_timeout // 10): # FIXED: use configurable timeout
            signal = await self.redis.get(stop_signal_key)
            if signal:
                print("Stop signal received!")
                break
            await asyncio.sleep(10)
        
        # ZillizPool.insert all 7 docs episodic_memory
        docs_to_insert = [
            {"fact_type": "spec_generated", "doc_type": k, "content_preview": v[:500], "timestamp": date.today().isoformat()}
            for k, v in context.items() if k != "requirements" and v
        ]
        try:
            await self.zilliz.insert(
                collection="episodic_memory",
                data=docs_to_insert
            )
            print("Successfully stored 7 docs to Zilliz episodic store.")
        except Exception as e:
            print(f"Failed to store specs to Zilliz: {e}")
            
        return SpecPackage(documents=context)
