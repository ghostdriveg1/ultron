from pydantic import BaseModel, Field
from typing import List, Dict, Any

class MassBalanceInput(BaseModel):
    streams: List[Dict[str, Any]] = Field(..., description="List of streams with flow rates and compositions")
    components: List[str] = Field(..., description="List of chemical components in the system")
    steady_state: bool = Field(default=True, description="Assume steady-state system (accumulation = 0)")

    model_config = {"extra": "forbid"}

class MassBalanceOutput(BaseModel):
    solution: Dict[str, float] = Field(..., description="Computed flow rates and compositions for all streams")
    closure_error_percent: float = Field(..., description="Percent error in the overall mass balance closure")
    dof: int = Field(..., description="Degrees of freedom in the system")

    model_config = {"extra": "forbid"}
