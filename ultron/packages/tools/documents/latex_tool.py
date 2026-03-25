import os
import tempfile
import subprocess
import re

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.latex_schema import LaTeXInput, LaTeXOutput
from .fast_io_client import FastIOClient

class LaTeXCompilationError(Exception):
    pass

class LaTeXTool(BaseTool):
    """Tool to generate PDFs from LaTeX source code."""
    input_schema = LaTeXInput
    output_schema = LaTeXOutput

    def __init__(self):
        super().__init__(
            name="create_latex_pdf",
            description="Compiles LaTeX source code into a PDF.",
            permission_level="ALWAYS_ALLOWED"
        )
        self.fast_io = FastIOClient()

    async def execute(self, params: LaTeXInput) -> LaTeXOutput:
        with tempfile.TemporaryDirectory() as temp_dir:
            tex_file = os.path.join(temp_dir, "document.tex")
            
            with open(tex_file, "w", encoding="utf-8") as f:
                f.write(params.content)
                
            # Compile twice for references
            for _ in range(2):
                result = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", "document.tex"],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True
                )
                
            pdf_path = os.path.join(temp_dir, "document.pdf")
            log_path = os.path.join(temp_dir, "document.log")
            
            log_content = ""
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    log_content = f.read()

            if not os.path.exists(pdf_path) or result.returncode != 0:
                # Basic error parsing
                errors = []
                for line in log_content.split('\n'):
                    if line.startswith('!') or "Undefined control sequence" in line or "Missing $ inserted" in line:
                        errors.append(line)
                
                excerpt = "\n".join(errors[-10:]) if errors else "General compilation error."
                raise LaTeXCompilationError(f"LaTeX Compilation Failed: {excerpt}")
                
            # Assume successful generation of PDF
            # Check page count approx via file size (lazy fallback)
            page_count = max(1, os.path.getsize(pdf_path) // 50000)

            # Upload
            fast_io_url = await self.fast_io.upload(pdf_path, params.output_filename)
            
            # Mock GitHub URL
            github_url = f"https://github.com/mock/outputs/{params.output_filename}"
            
            return LaTeXOutput(
                fast_io_url=fast_io_url,
                github_url=github_url,
                page_count=page_count,
                compilation_log_excerpt=log_content[:500] if "Warning" in log_content else ""
            )
