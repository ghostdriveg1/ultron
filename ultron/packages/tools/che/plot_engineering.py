import os
import tempfile
import plotly.graph_objects as go

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.plot_schema import PlotEngineeringInput, PlotOutput
from packages.tools.documents.fast_io_client import FastIOClient

class PlotEngineeringTool(BaseTool):
    """Generates publication-quality charts."""
    input_schema = PlotEngineeringInput
    output_schema = PlotOutput

    def __init__(self):
        super().__init__(
            name="create_engineering_plot",
            description="Creates high-quality plots for engineering data and uploads them.",
            permission_level="ALWAYS_ALLOWED"
        )
        self.fast_io = FastIOClient()

    async def execute(self, params: PlotEngineeringInput) -> PlotOutput:
        fig = go.Figure()
        
        # Group by label if needed
        labels = set(d.get("label", "Data") for d in params.data)
        
        for label in labels:
            x_vals = [d["x"] for d in params.data if d.get("label", "Data") == label]
            y_vals = [d["y"] for d in params.data if d.get("label", "Data") == label]
            
            if params.chart_type == "scatter":
                fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='markers', name=label))
            elif params.chart_type == "bar":
                fig.add_trace(go.Bar(x=x_vals, y=y_vals, name=label))
            else:
                fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name=label))
                
        fig.update_layout(
            title=params.title,
            xaxis_title=params.x_label,
            yaxis_title=params.y_label,
            template="plotly_white"
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "plot.png")
            fig.write_image(file_path)
            
            url = await self.fast_io.upload(file_path, "engineering_plot.png")
            
            return PlotOutput(fast_io_url=url)
