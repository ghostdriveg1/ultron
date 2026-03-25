from pydantic import BaseModel, Field
from typing import List, Dict

class VLEInput(BaseModel):
    components: List[str] = Field(..., description="List of component names")
    feed_composition: List[float] = Field(..., description="Mole fractions of components in the feed")
    temperature_k: float = Field(..., description="Temperature in Kelvin")
    pressure_pa: float = Field(..., description="Pressure in Pascals")

    model_config = {"extra": "forbid"}

class VLEOutput(BaseModel):
    vapor_fraction: float = Field(..., description="Molar fraction of the feed that is in the vapor phase")
    liquid_composition: List[float] = Field(..., description="Mole fractions in the liquid phase")
    vapor_composition: List[float] = Field(..., description="Mole fractions in the vapor phase")
    k_values: Dict[str, float] = Field(..., description="Distribution coefficients (K-values) for each component")

    model_config = {"extra": "forbid"}
