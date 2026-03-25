import os
import base64
from playwright.async_api import async_playwright, Page, BrowserContext

class ActionExecutor:
    """Executes atomic UI actions using Playwright."""
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context: BrowserContext = None
        self.page: Page = None

    async def initialize(self):
        if not self.playwright:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=False, # Often needs to be false for XVFB to work correctly if not natively headless
                env={**os.environ} # Inherits DISPLAY from XvfbManager
            )
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            self.page = await self.context.new_page()

    async def click(self, x: int, y: int) -> None:
        await self._ensure_init()
        await self.page.mouse.click(x, y)

    async def type_text(self, text: str) -> None:
        await self._ensure_init()
        await self.page.keyboard.type(text)

    async def scroll(self, x: int, y: int, direction: str, amount: int) -> None:
        await self._ensure_init()
        await self.page.mouse.move(x, y)
        if direction == "down":
            await self.page.mouse.wheel(0, amount)
        elif direction == "up":
            await self.page.mouse.wheel(0, -amount)

    async def screenshot(self) -> str:
        await self._ensure_init()
        bytes_data = await self.page.screenshot(full_page=False)
        return base64.b64encode(bytes_data).decode('utf-8')

    async def navigate(self, url: str) -> None:
        await self._ensure_init()
        await self.page.goto(url)

    async def _ensure_init(self):
        if not self.page:
            await self.initialize()

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
