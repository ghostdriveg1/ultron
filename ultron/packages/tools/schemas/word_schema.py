from pydantic import BaseModel, Field

class WordInput(BaseModel):
    title: str = Field(..., description="Title of the Word document")
    content: str = Field(..., description="Text content to be written to the Word document")
    output_filename: str = Field(..., description="Desired filename for the output document")

    model_config = {"extra": "forbid"}

class WordOutput(BaseModel):
    fast_io_url: str = Field(..., description="URL of the uploaded Word document on Fast.io")
    github_url: str = Field(..., description="URL of the committed Word document on GitHub")

    model_config = {"extra": "forbid"}
