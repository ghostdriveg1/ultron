"""
Ultron v3 — Escalation Module
Sends alerts to Ghost with interactive Discord buttons.
Waits for Ghost's response via bot.wait_for with timeout.
Logs timeout events to Redis JSONL archive.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Optional

import discord

logger = logging.getLogger("ultron.escalation")


async def send_ghost_alert(
    alert_type: str,
    context: dict,
    options: Optional[list[str]] = None,
    bot_token: str = "",
    channel_id: str = "",
    bot_instance: Optional[discord.Bot] = None,
    ghost_user_id: str = "",
) -> str:
    """
    Send an alert to Ghost with interactive action buttons.

    Args:
        alert_type: Type of alert (e.g., STUCK, ERROR, CIRCUIT_BREAKER)
        context: Dict with details (error, task, attempts, etc.)
        options: List of response options (default: RETRY, SKIP, ABORT)
        bot_token: Discord bot token (for REST fallback)
        channel_id: Channel to send alert to
        bot_instance: py-cord Bot instance for interactive responses
        ghost_user_id: Ghost's Discord user ID for interaction check

    Returns:
        Ghost's response string (or 'SKIP' on timeout)
    """
    if options is None:
        options = ["RETRY", "SKIP", "ABORT"]

    alert_id = str(uuid.uuid4())

    # Build embed
    error_detail = context.get("error", "Unknown error")
    task_info = context.get("task", "Unknown task")
    attempts = context.get("attempts", 0)

    embed = discord.Embed(
        title=f"🚨 Alert: {alert_type}",
        color=discord.Color.red(),
        timestamp=datetime.utcnow(),
    )
    embed.add_field(name="Task", value=task_info, inline=False)
    embed.add_field(name="Error", value=error_detail[:1024], inline=False)
    embed.add_field(name="Attempts", value=str(attempts), inline=True)
    embed.add_field(name="Alert ID", value=alert_id[:8], inline=True)
    embed.set_footer(text="Respond with a button below.")

    # Build action row with buttons
    view = discord.ui.View(timeout=86400)
    for option in options:
        style = {
            "RETRY": discord.ButtonStyle.primary,
            "SKIP": discord.ButtonStyle.secondary,
            "ABORT": discord.ButtonStyle.danger,
        }.get(option, discord.ButtonStyle.secondary)

        button = discord.ui.Button(
            label=option,
            custom_id=f"escalation:{alert_id}:{option}",
            style=style,
        )
        view.add_item(button)

    # ─── Interactive path: use bot instance ───────────────────
    if bot_instance and channel_id:
        try:
            channel = bot_instance.get_channel(int(channel_id))
            if not channel or not isinstance(channel, discord.TextChannel):
                channel = await bot_instance.fetch_channel(int(channel_id))

            alert_msg = await channel.send(embed=embed, view=view)

            # Wait for Ghost's button interaction
            def interaction_check(interaction: discord.Interaction) -> bool:
                if interaction.type != discord.InteractionType.component:
                    return False
                if ghost_user_id and str(interaction.user.id) != ghost_user_id:
                    return False
                if interaction.message and interaction.message.id != alert_msg.id:
                    return False
                return True

            try:
                interaction = await bot_instance.wait_for(
                    "interaction",
                    check=interaction_check,
                    timeout=86400,  # 24 hours
                )

                # Parse the custom_id: "escalation:{alert_id}:{OPTION}"
                custom_id = interaction.data.get("custom_id", "")
                choice = custom_id.split(":")[-1] if ":" in custom_id else "SKIP"

                # Acknowledge the interaction
                await interaction.response.send_message(
                    f"✅ Acknowledged: **{choice}**", ephemeral=True
                )

                logger.info(f"Escalation {alert_id}: Ghost chose {choice}")
                return choice

            except TimeoutError:
                # Log timeout to Redis JSONL
                timeout_entry = {
                    "alert_id": alert_id,
                    "alert_type": alert_type,
                    "context": context,
                    "timestamp": datetime.utcnow().isoformat(),
                    "result": "TIMEOUT",
                }

                try:
                    from packages.infrastructure.redis_client import UltronRedis
                    redis = UltronRedis()
                    timeout_key = f"escalations:timeout:{alert_id}.jsonl"
                    await redis.set(timeout_key, json.dumps(timeout_entry))
                    logger.info(f"Logged escalation timeout to {timeout_key}")
                except Exception as redis_err:
                    logger.error(f"Failed to log timeout to Redis: {redis_err}")

                logger.warning(
                    f"Escalation {alert_id} timed out after 24h — returning SKIP"
                )
                return "SKIP"

        except Exception as e:
            logger.error(f"Interactive escalation failed: {e}")
            # Fall through to REST fallback

    # ─── REST fallback: send plain message ────────────────────
    if bot_token and channel_id:
        import httpx

        DISCORD_API = "https://discord.com/api/v10"
        message = (
            f"🚨 **Alert: {alert_type}**\n\n"
            f"**Task:** {task_info}\n"
            f"**Error:** {error_detail}\n"
            f"**Attempts:** {attempts}\n\n"
            f"**Options:** {' | '.join(f'`{o}`' for o in options)}\n"
            f"_Reply with one of the options above._"
        )

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    f"{DISCORD_API}/channels/{channel_id}/messages",
                    headers={
                        "Authorization": f"Bot {bot_token}",
                        "Content-Type": "application/json",
                    },
                    json={"content": message},
                )
        except Exception as e:
            logger.error(f"Failed to send REST alert: {e}")

    logger.warning(
        f"Escalation alert {alert_id}: {alert_type} — "
        f"no bot instance, returning SKIP"
    )
    return "SKIP"
