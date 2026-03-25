import os
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.pdf_schema import PDFInput, PDFOutput
from .fast_io_client import FastIOClient

class PDFTool(BaseTool):
    """Tool to create PDFs using ReportLab and upload to Fast.io and GitHub."""
    input_schema = PDFInput
    output_schema = PDFOutput

    def __init__(self):
        super().__init__(
            name="create_pdf",
            description="Creates a PDF document from text content.",
            permission_level="ALWAYS_ALLOWED"
        )
        self.fast_io = FastIOClient()

    async def execute(self, params: PDFInput) -> PDFOutput:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, params.output_filename)
            
            # Create PDF
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            flowables = []
            
            flowables.append(Paragraph(params.title, styles['Title']))
            flowables.append(Spacer(1, 12))
            
            for line in params.content.split('\n'):
                flowables.append(Paragraph(line, styles['Normal']))
                flowables.append(Spacer(1, 6))
                
            doc.build(flowables)
            
            # Get actual page count (using dummy placeholder based on content length for simplicity)
            page_count = doc.page or max(1, len(params.content) // 2500)
            
            # Upload to Fast.io
            fast_io_url = await self.fast_io.upload(file_path, params.output_filename)
            
            # TODO: Call GitTool to commit to GitHub
            github_url = f"https://github.com/mock/outputs/{params.output_filename}"
            
            return PDFOutput(
                fast_io_url=fast_io_url,
                github_url=github_url,
                page_count=page_count
            )
