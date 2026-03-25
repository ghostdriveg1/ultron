import CoolProp.CoolProp as CP

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.thermo_schema import ThermoInput, ThermoOutput

class ThermoCalcTool(BaseTool):
    """Computes thermodynamic properties using CoolProp."""
    input_schema = ThermoInput
    output_schema = ThermoOutput

    def __init__(self):
        super().__init__(
            name="calc_thermo_properties",
            description="Calculates thermodynamic properties (Cp, H, S, Phase) using CoolProp.",
            permission_level="ALWAYS_ALLOWED"
        )

    async def execute(self, params: ThermoInput) -> ThermoOutput:
        fluid = params.fluid
        T = params.temperature_k
        P = params.pressure_pa
        
        try:
            # PropsSI signature: Output, Name1, Prop1, Name2, Prop2, Fluid
            cp = CP.PropsSI('C', 'T', T, 'P', P, fluid)
            h = CP.PropsSI('H', 'T', T, 'P', P, fluid)
            s = CP.PropsSI('S', 'T', T, 'P', P, fluid)
            
            # Phase is returned as an integer index, we can map basic ones or use PhaseSI
            phase_str = CP.PhaseSI('T', T, 'P', P, fluid)
            
            # Approximating G = H - TS
            g = h - (T * s)
            
            return ThermoOutput(
                cp=float(cp),
                h=float(h),
                s=float(s),
                g=float(g),
                phase=phase_str
            )
        except Exception as e:
            raise ValueError(f"CoolProp calculation failed: {str(e)}")
