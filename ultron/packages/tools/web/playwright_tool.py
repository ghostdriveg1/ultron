import base64
from playwright.async_api import async_playwright

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.playwright_schema import PlaywrightInput, PlaywrightOutput

class PlaywrightTool(BaseTool):
    """Automates browser interactions using Playwright."""
    input_schema = PlaywrightInput
    output_schema = PlaywrightOutput

    def __init__(self):
        super().__init__(
            name="browser_action",
            description="Launches a headless browser to navigate and interact with a webpage.",
            permission_level="GHOST_CONFIRM",
            requires_ghost_confirm=True
        )

    async def execute(self, params: PlaywrightInput) -> PlaywrightOutput:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            await page.goto(params.url)
            
            for action in params.actions:
                atype = action.get("type")
                selector = action.get("selector")
                
                if atype == "click" and selector:
                    await page.click(selector)
                elif atype == "type" and selector:
                    val = action.get("value", "")
                    await page.fill(selector, val)
                elif atype == "wait":
                    await page.wait_for_timeout(action.get("value", 1000))
                    
            # Take screenshot
            screenshot_bytes = await page.screenshot(full_page=False)
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            page_title = await page.title()
            current_url = page.url
            
            await browser.close()
            
            return PlaywrightOutput(
                screenshot_base64=screenshot_b64,
                page_title=page_title,
                current_url=current_url
            )
