import os
import logging
from packages.brain.key_rotation.provider_clients import GeminiClient

logger = logging.getLogger(__name__)

class DeepWikiGenerator:
    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client

    async def generate_module_doc(self, file_path: str, source_code: str) -> str:
        prompt = (
            f"Generate a structured Markdown documentation for this Python module.\n"
            f"File: {file_path}\n"
            f"Source code:\n{source_code}"
        )
        try:
            return await self.gemini_client.generate(prompt=prompt, system_prompt="You are a technical documenter.")
        except Exception as e:
            logger.error(f"Failed to generate doc for {file_path}: {e}")
            return ""

    async def update_wiki(self, repo_path: str, output_dir: str = "docs/wiki") -> int:
        count = 0
        target_dir = os.path.join(repo_path, output_dir)
        os.makedirs(target_dir, exist_ok=True)
        
        for root, _, files in os.walk(repo_path):
            if "node_modules" in root or ".git" in root or "venv" in root:
                continue
                
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            source = f.read()
                        
                        doc = await self.generate_module_doc(full_path, source)
                        if doc:
                            rel_path = os.path.relpath(full_path, repo_path)
                            doc_name = rel_path.replace("/", "_").replace("\\", "_").replace(".py", ".md")
                            doc_path = os.path.join(target_dir, doc_name)
                            
                            with open(doc_path, "w", encoding="utf-8") as out_f:
                                out_f.write(doc)
                            count += 1
                    except Exception:
                        pass
        return count
