from pint import UnitRegistry

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.unit_convert_schema import UnitConvertInput, UnitConvertOutput

class UnitConvertTool(BaseTool):
    """Converts engineering units using pint."""
    input_schema = UnitConvertInput
    output_schema = UnitConvertOutput

    def __init__(self):
        super().__init__(
            name="convert_units",
            description="Converts physical quantities between different engineering units.",
            permission_level="ALWAYS_ALLOWED"
        )
        self.ureg = UnitRegistry()

    async def execute(self, params: UnitConvertInput) -> UnitConvertOutput:
        try:
            qty = params.value * self.ureg(params.from_unit)
            converted = qty.to(params.to_unit)
            
            factor = converted.magnitude / params.value if params.value != 0 else 0
            
            return UnitConvertOutput(
                result=float(converted.magnitude),
                from_unit=params.from_unit,
                to_unit=params.to_unit,
                factor=factor
            )
        except Exception as e:
            raise ValueError(f"Unit conversion failed: {str(e)}")
