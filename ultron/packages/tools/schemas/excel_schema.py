from pydantic import BaseModel, Field
from typing import List, Any

class ExcelInput(BaseModel):
    data: List[List[Any]] = Field(..., description="2D list representing the rows and columns of the spreadsheet")
    output_filename: str = Field(..., description="Desired filename for the output Excel document")
    sheet_name: str = Field(default="Sheet1", description="Name of the main worksheet")

    model_config = {"extra": "forbid"}

class ExcelOutput(BaseModel):
    fast_io_url: str = Field(..., description="URL of the uploaded Excel document on Fast.io")
    github_url: str = Field(..., description="URL of the committed Excel document on GitHub")
    row_count: int = Field(..., description="Number of rows written")

    model_config = {"extra": "forbid"}
