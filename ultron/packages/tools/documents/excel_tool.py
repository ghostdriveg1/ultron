import os
import tempfile
from openpyxl import Workbook

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.excel_schema import ExcelInput, ExcelOutput
from .fast_io_client import FastIOClient

class ExcelTool(BaseTool):
    """Tool to create Excel spreadsheets from 2D data lists."""
    input_schema = ExcelInput
    output_schema = ExcelOutput

    def __init__(self):
        super().__init__(
            name="create_excel_doc",
            description="Creates an Excel spreadsheet from a 2D list of data.",
            permission_level="ALWAYS_ALLOWED"
        )
        self.fast_io = FastIOClient()

    async def execute(self, params: ExcelInput) -> ExcelOutput:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, params.output_filename)
            
            # Create Excel
            wb = Workbook()
            ws = wb.active
            ws.title = params.sheet_name
            
            row_count = 0
            for row in params.data:
                ws.append(row)
                row_count += 1
                
            wb.save(file_path)
            
            # Upload
            fast_io_url = await self.fast_io.upload(file_path, params.output_filename)
            
            # Mock GitHub URL
            github_url = f"https://github.com/mock/outputs/{params.output_filename}"
            
            return ExcelOutput(
                fast_io_url=fast_io_url,
                github_url=github_url,
                row_count=row_count
            )
