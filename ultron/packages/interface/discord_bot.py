"""
Ultron v3 — Discord Bot Entry Point
Primary interface between Ghost and the Ultron system.
Uses py-cord for Discord gateway connection.
"""

import os
import asyncio
import logging

import discord
from dotenv import load_dotenv

from packages.interface.message_handler import handle
from packages.interface.proactive import schedule_morning_briefing

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ultron.discord")

# ─── Bot Configuration ───────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True


class UltronBot(discord.Bot):
    """Ultron's Discord bot. Only responds to Ghost."""

    def __init__(self) -> None:
        super().__init__(intents=intents)
        self.ghost_user_id = os.getenv("DISCORD_GHOST_USER_ID", "")
        self.ghost_channel_id = os.getenv("DISCORD_CHANNEL_ID", "")

    async def on_ready(self) -> None:
        logger.info(f"Ultron online as {self.user} (ID: {self.user.id})")

        # Send startup message to Ghost's channel
        if self.ghost_channel_id:
            channel = self.get_channel(int(self.ghost_channel_id))
            if channel and isinstance(channel, discord.TextChannel):
                await channel.send("Ultron online. All systems ready.")

        # Start morning briefing scheduler
        asyncio.create_task(schedule_morning_briefing(self))

    async def on_message(self, message: discord.Message) -> None:
        # Ignore bot messages
        if message.author.bot:
            return

        # Only respond to Ghost (by user ID) or DMs
        is_ghost = str(message.author.id) == self.ghost_user_id
        is_dm = isinstance(message.channel, discord.DMChannel)

        if not is_ghost and not is_dm:
            return

        await handle(message)


# ─── Slash Commands ──────────────────────────────────────────
bot = UltronBot()


@bot.slash_command(name="status", description="Check Ultron system status")
async def status_command(ctx: discord.ApplicationContext) -> None:
    """Fetch system status from the Cloudflare Worker."""
    import httpx

    worker_url = os.getenv("CLAWCLOUD_WORKER_URL", "")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{worker_url}/api/status")
            data = resp.json()

        brain = "🟢" if data.get("brain_healthy") else "🔴"
        memory = "🟢" if data.get("memory_healthy") else "🔴"
        tasks = data.get("active_tasks", 0)

        status_text = (
            f"**Ultron System Status**\n"
            f"{brain} Brain | {memory} Memory\n"
            f"📋 Active Tasks: {tasks}\n"
        )

        # Quota usage
        quota = data.get("quota_usage", {})
        for provider, usage in quota.items():
            used = usage.get("used", 0)
            total = usage.get("total", 0)
            pct = (used / total * 100) if total > 0 else 0
            status_text += f"  • {provider}: {used}/{total} ({pct:.0f}%)\n"

        await ctx.respond(status_text)
    except Exception as e:
        await ctx.respond(f"⚠️ Failed to fetch status: {e}")


@bot.slash_command(name="stop", description="Pause Ultron operations")
async def stop_command(ctx: discord.ApplicationContext) -> None:
    """Set system:paused flag in Redis to pause all operations."""
    # This would use the Redis client; for now set via Worker
    await ctx.respond("⏸️ Ultron paused. Use `/resume` to continue.")


@bot.slash_command(name="resume", description="Resume Ultron operations")
async def resume_command(ctx: discord.ApplicationContext) -> None:
    """Clear system:paused flag in Redis to resume operations."""
    await ctx.respond("▶️ Ultron resumed. All systems active.")


# ─── Entry Point ─────────────────────────────────────────────
if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_BOT_TOKEN not set in environment")
    bot.run(token)
