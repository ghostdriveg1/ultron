from pydantic import BaseModel, Field
from typing import List, Dict, Any

class PlotEngineeringInput(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="List of data points containing x, y, label")
    chart_type: str = Field(..., description="Type of chart (e.g., 'scatter', 'line', 'bar')")
    title: str = Field(default="Engineering Plot", description="Chart title")
    x_label: str = Field(default="X-Axis", description="X-axis label")
    y_label: str = Field(default="Y-Axis", description="Y-axis label")

    model_config = {"extra": "forbid"}

class PlotOutput(BaseModel):
    fast_io_url: str = Field(..., description="URL of the generated plot image on Fast.io")

    model_config = {"extra": "forbid"}
