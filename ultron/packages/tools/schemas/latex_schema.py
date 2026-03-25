from pydantic import BaseModel, Field

class LaTeXInput(BaseModel):
    content: str = Field(..., description="Full LaTeX document content, including preamble and body")
    output_filename: str = Field(..., description="Desired filename for the output PDF (must end in .pdf)")
    auto_fix_errors: bool = Field(default=True, description="Whether to attempt automatic fixing of compilation errors")

    model_config = {"extra": "forbid"}

class LaTeXOutput(BaseModel):
    fast_io_url: str = Field(..., description="URL of the compiled PDF on Fast.io")
    github_url: str = Field(..., description="URL of the committed PDF on GitHub")
    page_count: int = Field(..., description="Number of pages in the generated PDF")
    compilation_log_excerpt: str = Field(default="", description="Excerpt from the pdflatex log if there were warnings")

    model_config = {"extra": "forbid"}
