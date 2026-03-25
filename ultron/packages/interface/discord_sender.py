"""
Ultron v3 — Discord Sender
Sends messages to Discord channels via REST API (no bot instance required).
Handles message splitting, file notifications, progress updates, and morning briefings.
"""

import logging
from typing import Optional

import httpx

logger = logging.getLogger("ultron.sender")


class DiscordSender:
    """Send messages to Discord via REST API using bot token."""

    DISCORD_API = "https://discord.com/api/v10"
    MAX_LENGTH = 1990  # Discord's 2000 char limit with margin

    def __init__(self, bot_token: str, default_channel_id: str = "") -> None:
        self.bot_token = bot_token
        self.default_channel_id = default_channel_id

    async def send_message(
        self, content: str, channel_id: Optional[str] = None
    ) -> None:
        """Send a simple message to a Discord channel."""
        cid = channel_id or self.default_channel_id
        if not cid:
            logger.error("No channel_id provided and no default set")
            return

        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(
                f"{self.DISCORD_API}/channels/{cid}/messages",
                headers={
                    "Authorization": f"Bot {self.bot_token}",
                    "Content-Type": "application/json",
                },
                json={"content": content},
            )

    async def send_split_message(
        self, content: str, channel_id: str
    ) -> None:
        """
        Split a long message into chunks that respect Discord's 2000 char limit.
        Never splits inside code blocks. Prefixes each chunk with [N/Total].
        """
        if len(content) <= self.MAX_LENGTH:
            await self.send_message(content, channel_id)
            return

        chunks: list[str] = []
        remaining = content
        in_code_block = False

        while remaining:
            if len(remaining) <= self.MAX_LENGTH:
                chunks.append(remaining)
                break

            # Find split point
            split_at = self.MAX_LENGTH

            # Check for open code blocks
            segment = remaining[:split_at]
            code_block_count = segment.count("```")
            in_code_block = code_block_count % 2 == 1

            if in_code_block:
                # Don't split inside code block — find the last ``` before limit
                last_fence = segment.rfind("```")
                if last_fence > 0:
                    split_at = last_fence

            # Try to split on word boundary
            space_idx = remaining.rfind(" ", 0, split_at)
            newline_idx = remaining.rfind("\n", 0, split_at)
            best_split = max(space_idx, newline_idx)

            if best_split > split_at // 2:
                split_at = best_split

            chunks.append(remaining[:split_at])
            remaining = remaining[split_at:].lstrip()

        total = len(chunks)
        for i, chunk in enumerate(chunks, 1):
            prefixed = f"[{i}/{total}] {chunk}"
            await self.send_message(prefixed, channel_id)

    async def send_file_notification(
        self,
        filename: str,
        fast_io_url: str,
        github_url: str,
        channel_id: Optional[str] = None,
    ) -> None:
        """Send a formatted file-ready notification with download links."""
        content = (
            f"📄 **File Ready:** `{filename}`\n"
            f"⬇️ Download: {fast_io_url}\n"
            f"🔗 GitHub: {github_url}"
        )
        await self.send_message(content, channel_id)

    async def send_progress_update(
        self,
        task: str,
        phase: str,
        percent: int,
        channel_id: Optional[str] = None,
    ) -> None:
        """Send a progress bar update using block characters."""
        filled = int(percent / 5)
        empty = 20 - filled
        bar = "█" * filled + "░" * empty

        content = (
            f"🔄 **{task}**\n"
            f"Phase: {phase}\n"
            f"Progress: {bar} {percent}%"
        )
        await self.send_message(content, channel_id)

    async def send_morning_briefing(
        self, summary: dict, channel_id: Optional[str] = None
    ) -> None:
        """Send the daily morning briefing at 8AM IST."""
        tasks_done = summary.get("tasks_completed", 0)
        tasks_pending = summary.get("tasks_pending", 0)
        memory_count = summary.get("memory_entries", 0)
        uptime = summary.get("uptime_hours", 0)
        highlights = summary.get("highlights", [])

        content = (
            f"☀️ **Good Morning, Ghost!**\n\n"
            f"📊 **Yesterday's Summary:**\n"
            f"  • Tasks completed: {tasks_done}\n"
            f"  • Tasks pending: {tasks_pending}\n"
            f"  • Memory entries: {memory_count}\n"
            f"  • System uptime: {uptime:.1f}h\n"
        )

        if highlights:
            content += "\n🌟 **Highlights:**\n"
            for h in highlights:
                content += f"  • {h}\n"

        content += "\n_Ready for today's instructions._"

        await self.send_message(content, channel_id)
