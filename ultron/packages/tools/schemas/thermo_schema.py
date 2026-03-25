from pydantic import BaseModel, Field

class ThermoInput(BaseModel):
    temperature_k: float = Field(..., description="Temperature in Kelvin")
    pressure_pa: float = Field(..., description="Pressure in Pascals")
    fluid: str = Field(..., description="CoolProp fluid name (e.g., 'Water', 'R134a')")

    model_config = {"extra": "forbid"}

class ThermoOutput(BaseModel):
    cp: float = Field(..., description="Specific heat capacity at constant pressure (J/kg-K)")
    h: float = Field(..., description="Specific enthalpy (J/kg)")
    s: float = Field(..., description="Specific entropy (J/kg-K)")
    g: float = Field(..., description="Specific Gibbs free energy (J/kg)")
    phase: str = Field(..., description="Phase of the fluid (e.g., 'liquid', 'gas', 'supercritical')")

    model_config = {"extra": "forbid"}
