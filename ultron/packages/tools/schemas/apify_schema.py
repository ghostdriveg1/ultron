from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ApifyInput(BaseModel):
    actor_id: str = Field(..., description="The Apify actor ID to invoke")
    run_input: Dict[str, Any] = Field(..., description="Input payload for the Apify actor")

    model_config = {"extra": "forbid"}

class ApifyOutput(BaseModel):
    results: List[Dict[str, Any]] = Field(..., description="List of results returned by the actor")

    model_config = {"extra": "forbid"}
