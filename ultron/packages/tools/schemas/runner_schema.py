from pydantic import BaseModel, Field
from typing import Literal

class RunnerInput(BaseModel):
    code: str = Field(..., description="Code content to execute in the sandbox")
    language: Literal["python", "javascript"] = Field(..., description="Language runtime to use")
    timeout_seconds: int = Field(default=30, description="Execution timeout in seconds")

    model_config = {"extra": "forbid"}

class RunnerOutput(BaseModel):
    stdout: str = Field(..., description="Standard output from the sandbox")
    stderr: str = Field(..., description="Standard error from the sandbox")
    exit_code: int = Field(..., description="Process exit code")
    duration_ms: int = Field(..., description="Execution duration in milliseconds")

    model_config = {"extra": "forbid"}
