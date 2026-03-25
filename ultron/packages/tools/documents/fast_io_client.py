import os
import httpx

class FastIOUploadError(Exception):
    pass

class FastIOClient:
    """Client for uploading files to Fast.io API."""
    def __init__(self):
        self.api_key = os.getenv("FASTIO_KEY")
        self.base_url = "https://api.fast.io/v1/upload" # placeholder API endpoint

    async def upload(self, file_path: str, filename: str) -> str:
        """Uploads a file to Fast.io and returns the permanent URL."""
        if not self.api_key:
            # Fallback for local dev without key
            return f"https://mock.fast.io/files/{filename}"
            
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                with open(file_path, "rb") as f:
                    files = {"file": (filename, f)}
                    response = await client.post(self.base_url, headers=headers, files=files)
                
                response.raise_for_status()
                data = response.json()
                
                if "url" in data:
                    return data["url"]
                else:
                    raise FastIOUploadError(f"Unexpected response format: {data}")
            except httpx.HTTPError as e:
                raise FastIOUploadError(f"HTTP error during upload: {e}")
            except Exception as e:
                raise FastIOUploadError(f"Upload failed: {str(e)}")
