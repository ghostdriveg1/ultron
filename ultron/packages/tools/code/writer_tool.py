import os

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.writer_schema import WriterInput, WriterOutput
# In a real impl, this would import the Gemini client from Phase 1-4
# from packages.interface.gemini_client import GeminiClient

class MockGeminiClient:
    async def generate_code(self, prompt: str, system_instruction: str) -> str:
        # Placeholder mock for generation
        return f"# Generated based on prompt:\n# {prompt}\n\ndef example():\n    pass\n"

class WriterTool(BaseTool):
    """Generates code using Gemini and writes it to a file, applying style guides."""
    input_schema = WriterInput
    output_schema = WriterOutput

    def __init__(self):
        super().__init__(
            name="write_code",
            description="Generates new code using Gemini based on instructions and style guides.",
            permission_level="ENTROPY_CHECKED"
        )
        self.llm = MockGeminiClient()

    def _get_style_guide(self, language: str) -> str:
        guide_path = f"skills/coding/{language}/SKILL.md"
        if os.path.exists(guide_path):
            with open(guide_path, 'r', encoding='utf-8') as f:
                return f.read()
        return "Write clean, highly-readable code."

    async def execute(self, params: WriterInput) -> WriterOutput:
        style_guide = self._get_style_guide(params.language)
        system_instruction = f"You are an expert {params.language} developer. Follow this style guide strictly:\n{style_guide}"
        
        generated_code = await self.llm.generate_code(params.prompt, system_instruction)
        
        # Clean up markdown formatting if present
        if generated_code.startswith("```"):
            lines = generated_code.split('\n')
            if len(lines) > 2:
                generated_code = '\n'.join(lines[1:-1])

        os.makedirs(os.path.dirname(os.path.abspath(params.file_path)), exist_ok=True)
        with open(params.file_path, 'w', encoding='utf-8') as f:
            f.write(generated_code)
            
        return WriterOutput(
            code=generated_code,
            language=params.language,
            file_path=params.file_path
        )
