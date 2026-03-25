from pydantic import BaseModel, Field

class PDFInput(BaseModel):
    title: str = Field(..., description="Title of the PDF document")
    content: str = Field(..., description="Markdown or text content to be converted to PDF")
    output_filename: str = Field(..., description="Desired filename for the output PDF")

    model_config = {"extra": "forbid"}

class PDFOutput(BaseModel):
    fast_io_url: str = Field(..., description="URL of the uploaded PDF on Fast.io")
    github_url: str = Field(..., description="URL of the committed PDF on GitHub")
    page_count: int = Field(..., description="Number of pages in the generated PDF")

    model_config = {"extra": "forbid"}
