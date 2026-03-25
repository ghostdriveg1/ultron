from pydantic import BaseModel, Field
from typing import List

class Slide(BaseModel):
    title: str = Field(..., description="Title of the slide")
    content: str = Field(..., description="Text content or bullet points for the slide")

class PPTXInput(BaseModel):
    slides: List[Slide] = Field(..., description="List of slides to include in the presentation")
    output_filename: str = Field(..., description="Desired filename for the output PPTX document")

    model_config = {"extra": "forbid"}

class PPTXOutput(BaseModel):
    fast_io_url: str = Field(..., description="URL of the uploaded PPTX document on Fast.io")
    github_url: str = Field(..., description="URL of the committed PPTX document on GitHub")
    slide_count: int = Field(..., description="Number of slides in the generated presentation")

    model_config = {"extra": "forbid"}
