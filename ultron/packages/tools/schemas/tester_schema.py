from pydantic import BaseModel, Field
from typing import List

class TesterInput(BaseModel):
    test_path: str = Field(..., description="Path to the test file or directory to execute")
    framework: str = Field(default="pytest", description="Testing framework to use (pytest, jest, etc.)")

    model_config = {"extra": "forbid"}

class TesterOutput(BaseModel):
    passed: int = Field(..., description="Number of passing tests")
    failed: int = Field(..., description="Number of failing tests")
    coverage_percent: float = Field(..., description="Code coverage percentage")
    failures: List[str] = Field(..., description="List of failure messages or stack traces")

    model_config = {"extra": "forbid"}
