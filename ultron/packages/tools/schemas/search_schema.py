from pydantic import BaseModel, Field
from typing import List, Dict, Any

class SearchInput(BaseModel):
    query: str = Field(..., description="Query string to search the web")

    model_config = {"extra": "forbid"}

class SearchOutput(BaseModel):
    results: List[Dict[str, Any]] = Field(..., description="List of search results containing title, url, snippet")

    model_config = {"extra": "forbid"}
