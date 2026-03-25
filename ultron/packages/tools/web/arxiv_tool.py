import httpx
import urllib.parse
import xml.etree.ElementTree as ET

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.arxiv_schema import ArxivInput, ArxivOutput

class ArxivTool(BaseTool):
    """Searches academic papers on ArXiv."""
    input_schema = ArxivInput
    output_schema = ArxivOutput

    def __init__(self):
        super().__init__(
            name="search_arxiv",
            description="Searches ArXiv for academic papers and returns metadata.",
            permission_level="ALWAYS_ALLOWED"
        )
        self.base_url = "http://export.arxiv.org/api/query"

    async def execute(self, params: ArxivInput) -> ArxivOutput:
        query = urllib.parse.quote(params.query)
        url = f"{self.base_url}?search_query=all:{query}&max_results={params.max_results}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            
            xml_data = response.text
            
            # Parse Atom XML
            root = ET.fromstring(xml_data)
            
            # XML namespace definition for Atom
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            papers = []
            for entry in root.findall('atom:entry', ns):
                title = entry.find('atom:title', ns).text.strip()
                summary = entry.find('atom:summary', ns).text.strip()
                published = entry.find('atom:published', ns).text
                
                url_elem = entry.find("atom:link[@type='text/html']", ns)
                paper_url = url_elem.attrib['href'] if url_elem is not None else entry.find('atom:id', ns).text
                
                authors = [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)]
                
                papers.append({
                    "title": title.replace('\n', ' '),
                    "abstract": summary.replace('\n', ' '),
                    "authors": authors,
                    "url": paper_url,
                    "published": published
                })
                
            return ArxivOutput(papers=papers)
