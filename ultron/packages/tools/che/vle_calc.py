from thermo import Mixture

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.vle_schema import VLEInput, VLEOutput

class VLECalcTool(BaseTool):
    """Calculates Vapor-Liquid Equilibrium using thermo library."""
    input_schema = VLEInput
    output_schema = VLEOutput

    def __init__(self):
        super().__init__(
            name="calc_vle",
            description="Performs Vapor-Liquid Equilibrium calculations for mixtures.",
            permission_level="ALWAYS_ALLOWED"
        )

    async def execute(self, params: VLEInput) -> VLEOutput:
        try:
            m = Mixture(params.components, zs=params.feed_composition, T=params.temperature_k, P=params.pressure_pa)
            
            # Mixture automatically flashes at given T and P
            vf = m.V
            if vf is None:
                # If single phase, V is either 0 or 1. Let's deduce.
                vf = 1.0 if m.phase == 'g' else 0.0
                
            x = m.xs if m.xs else params.feed_composition
            y = m.ys if m.ys else params.feed_composition
            
            k_values = {}
            for i, comp in enumerate(params.components):
                # K = y/x
                k_val = y[i] / x[i] if x[i] > 1e-10 else 0.0
                k_values[comp] = k_val
                
            return VLEOutput(
                vapor_fraction=float(vf),
                liquid_composition=x,
                vapor_composition=y,
                k_values=k_values
            )
        except Exception as e:
            raise ValueError(f"VLE calculation failed: {str(e)}")
