"""
Ultron v3 — Proactive Module
Scheduled tasks: morning briefing at 8AM IST, weekly summaries.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

import discord

from packages.interface.discord_sender import DiscordSender

logger = logging.getLogger("ultron.proactive")

# IST = UTC+5:30
IST = timezone(timedelta(hours=5, minutes=30))


async def schedule_morning_briefing(bot: discord.Bot) -> None:
    """
    Asyncio loop that calculates seconds until next 8AM IST,
    sleeps, then sends the morning briefing. Repeats daily.
    """
    import os

    channel_id = os.getenv("DISCORD_CHANNEL_ID", "")
    bot_token = os.getenv("DISCORD_BOT_TOKEN", "")

    if not channel_id or not bot_token:
        logger.warning("Missing DISCORD_CHANNEL_ID or DISCORD_BOT_TOKEN — skipping briefing scheduler")
        return

    sender = DiscordSender(bot_token=bot_token, default_channel_id=channel_id)

    while True:
        try:
            now = datetime.now(IST)
            target = now.replace(hour=8, minute=0, second=0, microsecond=0)

            # If it's already past 8AM today, schedule for tomorrow
            if now >= target:
                target += timedelta(days=1)

            wait_seconds = (target - now).total_seconds()
            logger.info(f"Next morning briefing in {wait_seconds:.0f}s ({target.isoformat()})")

            await asyncio.sleep(wait_seconds)

            # Generate briefing summary
            summary = await generate_daily_summary()
            await sender.send_morning_briefing(summary, channel_id)

            logger.info("Morning briefing sent successfully")

        except asyncio.CancelledError:
            logger.info("Morning briefing scheduler cancelled")
            break
        except Exception as e:
            logger.error(f"Morning briefing error: {e}")
            await asyncio.sleep(60)  # Retry after 1 minute on error


async def generate_daily_summary() -> dict:
    """
    Generate a daily summary by reading system state.
    Stub implementation — reads state/SYSTEM_STATUS.md.
    """
    # TODO: Read from Redis and actual system state
    return {
        "tasks_completed": 0,
        "tasks_pending": 0,
        "memory_entries": 0,
        "uptime_hours": 0.0,
        "highlights": ["System initialized — awaiting first task"],
    }


async def generate_weekly_summary() -> str:
    """
    Generate a weekly summary by aggregating daily data.
    Stub implementation — reads state/SYSTEM_STATUS.md.
    """
    # TODO: Aggregate from Redis / Zilliz for the past 7 days
    return (
        "📊 **Weekly Summary**\n\n"
        "No data available yet. Weekly summaries will be generated "
        "once the system has been running for at least 7 days."
    )
