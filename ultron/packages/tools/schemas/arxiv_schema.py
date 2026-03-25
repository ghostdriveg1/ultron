from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ArxivInput(BaseModel):
    query: str = Field(..., description="Search query string for the ArXiv API")
    max_results: int = Field(default=5, description="Maximum number of papers to retrieve")

    model_config = {"extra": "forbid"}

class ArxivOutput(BaseModel):
    papers: List[Dict[str, Any]] = Field(..., description="List of papers with title, authors, abstract, url, published")

    model_config = {"extra": "forbid"}
