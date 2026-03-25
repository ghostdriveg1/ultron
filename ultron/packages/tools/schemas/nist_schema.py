from pydantic import BaseModel, Field
from typing import Optional

class NISTInput(BaseModel):
    compound: str = Field(..., description="Compound name or CAS registry number")
    temperature_k: float = Field(..., description="Temperature in Kelvin")
    pressure_pa: float = Field(default=101325.0, description="Pressure in Pascals")

    model_config = {"extra": "forbid"}

class NISTOutput(BaseModel):
    cp: Optional[float] = Field(None, description="Specific heat capacity at constant pressure (J/mol-K)")
    h: Optional[float] = Field(None, description="Enthalpy (kJ/mol)")
    s: Optional[float] = Field(None, description="Entropy (J/mol-K)")
    g: Optional[float] = Field(None, description="Gibbs free energy (kJ/mol)")

    model_config = {"extra": "forbid"}
