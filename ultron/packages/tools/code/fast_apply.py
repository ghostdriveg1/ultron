import ast
import subprocess
import os

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.fast_apply_schema import FastApplyInput, FastApplyOutput

class FastApplyTool(BaseTool):
    """Tool to precisely replace a snippet of code and verify syntax."""
    input_schema = FastApplyInput
    output_schema = FastApplyOutput

    def __init__(self):
        super().__init__(
            name="fast_apply",
            description="Replaces exactly one occurrence of old_content with new_content and validates syntax.",
            permission_level="ENTROPY_CHECKED"
        )

    async def execute(self, params: FastApplyInput) -> FastApplyOutput:
        if not os.path.exists(params.file_path):
            return FastApplyOutput(success=False, lines_changed=0, syntax_valid=False, error_message="File not found")

        with open(params.file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        count = content.count(params.old_content)
        if count == 0:
            return FastApplyOutput(success=False, lines_changed=0, syntax_valid=False, error_message="old_content not found in file")
        elif count > 1:
            return FastApplyOutput(success=False, lines_changed=0, syntax_valid=False, error_message="old_content matches multiple times. Must provide a unique block to replace.")

        new_full_content = content.replace(params.old_content, params.new_content)
        
        # Write temporarily to test syntax
        with open(params.file_path, 'w', encoding='utf-8') as f:
            f.write(new_full_content)

        # Check syntax
        is_valid = True
        error_msg = ""
        
        try:
            if params.file_path.endswith('.py'):
                ast.parse(new_full_content)
            elif params.file_path.endswith('.js') or params.file_path.endswith('.ts') or params.file_path.endswith('.tsx') or params.file_path.endswith('.jsx'):
                result = subprocess.run(['node', '--check', params.file_path], capture_output=True, text=True)
                if result.returncode != 0:
                    is_valid = False
                    error_msg = result.stderr
        except SyntaxError as e:
            is_valid = False
            error_msg = str(e)
            
        if not is_valid:
            # Revert changes
            with open(params.file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return FastApplyOutput(success=False, lines_changed=0, syntax_valid=False, error_message=f"Syntax Error: {error_msg}")
            
        lines_changed = len(params.new_content.split('\n'))
        return FastApplyOutput(success=True, lines_changed=lines_changed, syntax_valid=True)
