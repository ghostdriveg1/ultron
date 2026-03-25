from pydantic import BaseModel, Field
from typing import Literal

class WriterInput(BaseModel):
    prompt: str = Field(..., description="Instructions for generating the code")
    language: Literal["python", "javascript", "typescript"] = Field(..., description="Target language")
    file_path: str = Field(..., description="Path where the generated code should be saved")

    model_config = {"extra": "forbid"}

class WriterOutput(BaseModel):
    code: str = Field(..., description="The generated source code")
    language: str = Field(..., description="The language of the generated code")
    file_path: str = Field(..., description="The path where the code was written")

    model_config = {"extra": "forbid"}
