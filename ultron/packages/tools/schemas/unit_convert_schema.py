from pydantic import BaseModel, Field

class UnitConvertInput(BaseModel):
    value: float = Field(..., description="The numeric value to convert")
    from_unit: str = Field(..., description="The unit to convert from (e.g., 'kg/hr')")
    to_unit: str = Field(..., description="The unit to convert to (e.g., 'lb/min')")

    model_config = {"extra": "forbid"}

class UnitConvertOutput(BaseModel):
    result: float = Field(..., description="The converted value")
    from_unit: str = Field(..., description="The original unit")
    to_unit: str = Field(..., description="The target unit")
    factor: float = Field(..., description="The conversion factor applied")

    model_config = {"extra": "forbid"}
