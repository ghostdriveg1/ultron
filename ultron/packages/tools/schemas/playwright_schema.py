from pydantic import BaseModel, Field
from typing import List, Dict, Any

class PlaywrightInput(BaseModel):
    url: str = Field(..., description="URL to navigate to")
    actions: List[Dict[str, Any]] = Field(default=[], description="List of actions to perform (type, selector, value)")

    model_config = {"extra": "forbid"}

class PlaywrightOutput(BaseModel):
    screenshot_base64: str = Field(..., description="Base64 encoded string of the resulting screenshot PNG")
    page_title: str = Field(..., description="Title of the webpage after actions")
    current_url: str = Field(..., description="URL of the webpage after actions")

    model_config = {"extra": "forbid"}
