import asyncio
import httpx
import os

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.search_schema import SearchInput, SearchOutput

class SearchTool(BaseTool):
    """Performs web searches using multiple search engines."""
    input_schema = SearchInput
    output_schema = SearchOutput

    def __init__(self):
        super().__init__(
            name="search_web",
            description="Searches the web and aggregates results from Brave Search and DuckDuckGo.",
            permission_level="ALWAYS_ALLOWED"
        )

    async def _brave_search(self, query: str) -> list:
        api_key = os.getenv("BRAVE_SEARCH_KEY")
        if not api_key:
            return [{"title": f"Brave Mock Result for {query}", "url": "https://brave.mock", "snippet": "Mocked brave result."}]
            
        async with httpx.AsyncClient() as client:
            headers = {"Accept": "application/json", "X-Subscription-Token": api_key}
            try:
                # Basic invocation
                response = await client.get("https://api.search.brave.com/res/v1/web/search", params={"q": query}, headers=headers)
                response.raise_for_status()
                data = response.json()
                results = []
                for item in data.get("web", {}).get("results", [])[:5]:
                    results.append({
                        "title": item.get("title"),
                        "url": item.get("url"),
                        "snippet": item.get("description")
                    })
                return results
            except Exception:
                return []

    async def _ddg_search(self, query: str) -> list:
        # DDG HTML scraping or lite API is often blocked, using a mock for this Phase 5 stub
        return [{"title": f"DDG Mock Result for {query}", "url": "https://duckduckgo.mock", "snippet": "Mocked DDG result."}]

    async def execute(self, params: SearchInput) -> SearchOutput:
        brave_task = self._brave_search(params.query)
        ddg_task = self._ddg_search(params.query)
        
        results_lists = await asyncio.gather(brave_task, ddg_task)
        
        merged_results = []
        seen_urls = set()
        
        for results in results_lists:
            for item in results:
                if item["url"] not in seen_urls:
                    seen_urls.add(item["url"])
                    # Wrap in untrusted tags per spec
                    item["snippet"] = f"<WEB_CONTENT_UNTRUSTED>{item['snippet']}</WEB_CONTENT_UNTRUSTED>"
                    merged_results.append(item)
                    
        return SearchOutput(results=merged_results)
