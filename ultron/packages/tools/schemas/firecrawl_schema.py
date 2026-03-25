from pydantic import BaseModel, Field

class FirecrawlInput(BaseModel):
    url: str = Field(..., description="URL of the webpage to scrape and convert to markdown")

    model_config = {"extra": "forbid"}

class FirecrawlOutput(BaseModel):
    markdown: str = Field(..., description="Scraped webpage content in markdown format, stripped of injection patterns")
    url: str = Field(..., description="The URL that was scraped")
    title: str = Field(default="", description="Title of the scraped webpage")

    model_config = {"extra": "forbid"}
