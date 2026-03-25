import os
import httpx

class NotionClient:
    def __init__(self):
        self.token = os.getenv("NOTION_TOKEN")
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def create_page(self, parent_id: str, title: str, content: str) -> str:
        if not self.token:
            return ""
        data = {
            "parent": {"type": "page_id", "page_id": parent_id},
            "properties": {
                "title": [{"text": {"content": title}}]
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": content[:2000]}}]
                    }
                }
            ]
        }
        try:
            resp = httpx.post(f"{self.base_url}/pages", headers=self.headers, json=data)
            resp.raise_for_status()
            return resp.json().get("id", "")
        except Exception:
            return ""

    def update_page(self, page_id: str, content: str) -> None:
        if not self.token:
            return
        data = {
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": content[:2000]}}]
                    }
                }
            ]
        }
        try:
            httpx.patch(f"{self.base_url}/blocks/{page_id}/children", headers=self.headers, json=data)
        except Exception:
            pass

    def search_pages(self, query: str) -> list[dict]:
        if not self.token:
            return []
        data = {"query": query}
        try:
            resp = httpx.post(f"{self.base_url}/search", headers=self.headers, json=data)
            resp.raise_for_status()
            return resp.json().get("results", [])
        except Exception:
            return []
