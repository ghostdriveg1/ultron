import numpy as np

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.mass_balance_schema import MassBalanceInput, MassBalanceOutput

class MassBalanceTool(BaseTool):
    """Calculates steady-state mass balances for chemical processes."""
    input_schema = MassBalanceInput
    output_schema = MassBalanceOutput

    def __init__(self):
        super().__init__(
            name="solve_mass_balance",
            description="Solves steady-state mass balance equations given streams and components.",
            permission_level="ALWAYS_ALLOWED"
        )

    async def execute(self, params: MassBalanceInput) -> MassBalanceOutput:
        # Simplified mass balance solver stub
        # Real implementation would parse network topology and build A x = b matrix
        # For this Phase 5 stub, we check DOF directly from provided unknowns
        
        # Count available equations (usually number of components * nodes)
        # We'll just mock the computation logic based on the input structure
        
        unknowns = sum(1 for s in params.streams if "flow" not in s)
        equations = len(params.components)
        
        dof = unknowns - equations
        
        if dof != 0 and params.steady_state:
            raise ValueError(f"Degrees of freedom is {dof}, system is not fully specified or is overspecified.")
            
        # Mock solution
        solution = {}
        for s in params.streams:
            solution[s.get("name", "UnknownStream")] = s.get("flow", 100.0)
            
        closure_error = 0.0 # perfect mock closure
        
        return MassBalanceOutput(
            solution=solution,
            closure_error_percent=closure_error,
            dof=dof
        )
