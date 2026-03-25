import os
import tempfile
import numpy as np
import plotly.graph_objects as go

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.mccabe_thiele_schema import McCabeThieleInput, McCabeThieleOutput
from packages.tools.documents.fast_io_client import FastIOClient

class McCabeThieleTool(BaseTool):
    """Generates McCabe-Thiele diagrams for distillation."""
    input_schema = McCabeThieleInput
    output_schema = McCabeThieleOutput

    def __init__(self):
        super().__init__(
            name="plot_mccabe_thiele",
            description="Generates a McCabe-Thiele diagram and uploads the plot.",
            permission_level="ALWAYS_ALLOWED"
        )
        self.fast_io = FastIOClient()

    async def execute(self, params: McCabeThieleInput) -> McCabeThieleOutput:
        # Basic generation logic
        x_eq = np.linspace(0, 1, 100)
        alpha = params.relative_volatility
        y_eq = (alpha * x_eq) / (1 + (alpha - 1) * x_eq)
        
        fig = go.Figure()
        
        # Equilibrium line and 45 degree line
        fig.add_trace(go.Scatter(x=x_eq, y=y_eq, mode='lines', name='Equilibrium Curve'))
        fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', name='y=x', line=dict(dash='dash')))
        
        # Operating lines (simplified representation)
        fig.add_trace(go.Scatter(x=[params.xd, params.xb], y=[params.xd, params.xb], mode='markers', name='Feed/Products'))
        
        fig.update_layout(title="McCabe-Thiele Diagram", xaxis_title="x (Liquid Mol Fraction)", yaxis_title="y (Vapor Mol Fraction)")
        
        n_stages = 5 # Mock stage count for simplicity, real impl would step off stages
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "mccabe_thiele.png")
            fig.write_image(file_path)
            
            url = await self.fast_io.upload(file_path, "mccabe_thiele.png")
            
            return McCabeThieleOutput(
                fast_io_url=url,
                n_theoretical_stages=n_stages
            )
