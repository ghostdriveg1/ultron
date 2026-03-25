from pydantic import BaseModel, Field

class FastApplyInput(BaseModel):
    file_path: str = Field(..., description="Absolute path to the file to modify")
    old_content: str = Field(..., description="Exact string to replace (must appear exactly once)")
    new_content: str = Field(..., description="New string to replace old_content with")

    model_config = {"extra": "forbid"}

class FastApplyOutput(BaseModel):
    success: bool = Field(..., description="True if modification was successful")
    lines_changed: int = Field(..., description="Number of lines changed")
    syntax_valid: bool = Field(..., description="True if the resulting code is syntactically valid")
    error_message: str = Field(default="", description="Error details if modification failed")

    model_config = {"extra": "forbid"}
