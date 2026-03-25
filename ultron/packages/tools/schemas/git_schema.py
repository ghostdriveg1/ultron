from pydantic import BaseModel, Field
from typing import Literal

class GitInput(BaseModel):
    operation: Literal["commit", "push", "create_pr", "create_branch"] = Field(..., description="Git operation to perform")
    message: str = Field(default="", description="Commit message or PR description")
    branch_name: str = Field(default="", description="Name of the branch (for create_branch or PR base)")
    repo_path: str = Field(default=".", description="Path to the local repository")

    model_config = {"extra": "forbid"}

class GitOutput(BaseModel):
    success: bool = Field(..., description="True if the operation succeeded")
    commit_sha: str = Field(default="", description="SHA hash of the created commit")
    url: str = Field(default="", description="URL of the resulting artifact (e.g., PR link)")
    error_message: str = Field(default="", description="Error details if execution failed")

    model_config = {"extra": "forbid"}
