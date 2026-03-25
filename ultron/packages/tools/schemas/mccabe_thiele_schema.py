from pydantic import BaseModel, Field

class McCabeThieleInput(BaseModel):
    xf: float = Field(..., description="Feed mole fraction (light key)")
    xd: float = Field(..., description="Distillate mole fraction (light key)")
    xb: float = Field(..., description="Bottoms mole fraction (light key)")
    reflux_ratio: float = Field(..., description="Reflux ratio (L/D)")
    q: float = Field(..., description="Feed quality (q)")
    relative_volatility: float = Field(..., description="Relative volatility (alpha)")

    model_config = {"extra": "forbid"}

class McCabeThieleOutput(BaseModel):
    fast_io_url: str = Field(..., description="URL of the generated McCabe-Thiele diagram on Fast.io")
    n_theoretical_stages: int = Field(..., description="Number of theoretical stages required")

    model_config = {"extra": "forbid"}
