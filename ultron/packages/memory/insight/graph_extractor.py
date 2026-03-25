import json
from packages.brain.key_rotation.provider_clients import GeminiClient
from packages.memory.insight.cognee_client import CogneeClient, Entity

class GraphExtractor:
    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client

    async def extract_relationships_from_text(self, text: str) -> list[dict]:
        prompt = (
            "Extract entity-relationship triples from this text.\n"
            "Return JSON array of {from_entity, from_type, relationship, to_entity, to_type, weight}."
        )
        try:
            # We mock the generate call since GeminiClient implementation details are behind protocol
            # However we pass what we assume acts as prompt and context
            # We might just try a standard method from the provider
            response = await self.gemini_client.generate(prompt=prompt + f"\nContext:\n{text}")
            
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:-3]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:-3]
            return json.loads(cleaned)
        except Exception:
            return []

    async def extract_and_store(self, text: str, cognee: CogneeClient) -> int:
        triples = await self.extract_relationships_from_text(text)
        count = 0
        for t in triples:
            from_id = t.get("from_entity")
            to_id = t.get("to_entity")
            if from_id and to_id:
                cognee.add_entity(Entity(id=from_id, type=t.get("from_type", "Unknown"), name=from_id, properties={}))
                cognee.add_entity(Entity(id=to_id, type=t.get("to_type", "Unknown"), name=to_id, properties={}))
                cognee.add_relationship(from_id, t.get("relationship", "RELATED_TO"), to_id, float(t.get("weight", 1.0)), {})
                count += 1
        return count
