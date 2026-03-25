import subprocess
import json
import os

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.linter_schema import LinterInput, LinterOutput

class LinterTool(BaseTool):
    """Runs linters and type checkers on Python code."""
    input_schema = LinterInput
    output_schema = LinterOutput

    def __init__(self):
        super().__init__(
            name="run_linter",
            description="Runs pylint and mypy on a Python file to extract scores and errors.",
            permission_level="ALWAYS_ALLOWED"
        )

    async def execute(self, params: LinterInput) -> LinterOutput:
        pylint_score = 0.0
        mypy_errors = []
        issues = []

        if not os.path.exists(params.file_path):
            return LinterOutput(pylint_score=0.0, mypy_errors=["File not found"], issues=[f"Cannot lint nonexistent file: {params.file_path}"])

        # Pylint
        pylint_result = subprocess.run(
            ["pylint", params.file_path, "--output-format=json"], 
            capture_output=True, text=True
        )
        try:
            if pylint_result.stdout.strip():
                lint_data = json.loads(pylint_result.stdout)
                for item in lint_data:
                    issues.append(f"{item.get('line')}:{item.get('column')} [{item.get('message-id')}] {item.get('message')}")
                    # Approximate score calculation if pylint doesn't output it in JSON directly easily
            
            # Run text format just to get the explicit score from the output text
            text_result = subprocess.run(["pylint", params.file_path], capture_output=True, text=True)
            for line in text_result.stdout.split('\n'):
                if "Your code has been rated at" in line:
                    score_str = line.split('at')[1].split('/')[0].strip()
                    try:
                        pylint_score = float(score_str)
                    except ValueError:
                        pass
        except json.JSONDecodeError:
            issues.append("Failed to parse pylint output.")

        # Mypy
        # Usually mypy doesn't emit pure json unless using a custom formatter, but we can parse text or use mypy --output-format json in some plugins
        # Better to parse standard text format for simplicity if no specific json plugin is mandated
        mypy_result = subprocess.run(
            ["mypy", params.file_path], capture_output=True, text=True
        )
        for line in mypy_result.stdout.split('\n'):
            if "error:" in line:
                mypy_errors.append(line.strip())

        return LinterOutput(
            pylint_score=pylint_score,
            mypy_errors=mypy_errors,
            issues=issues
        )
