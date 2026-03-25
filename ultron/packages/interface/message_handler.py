"""
Ultron v3 — Message Handler
Forwards Ghost's messages to the Cloudflare Worker via the internal endpoint,
then dispatches to Python-side TaskDispatcher for actual execution.
"""

import os
import logging

import discord
import httpx

from packages.interface.escalation import send_ghost_alert

logger = logging.getLogger("ultron.handler")

WORKER_URL = os.getenv("CLAWCLOUD_WORKER_URL", "")
INTERNAL_AUTH_TOKEN = os.getenv("INTERNAL_AUTH_TOKEN", "")


async def handle(message: discord.Message) -> None:
    """
    Handle an incoming Discord message from Ghost.
    Shows typing indicator while forwarding to the Worker's internal endpoint.
    On instant mode, also runs Python-side TaskDispatcher for Phase 2 routing.
    """
    async with message.channel.typing():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    f"{WORKER_URL}/internal/task",
                    headers={
                        "Content-Type": "application/json",
                        "X-Ultron-Token": INTERNAL_AUTH_TOKEN,
                    },
                    json={
                        "content": message.content,
                        "channel_id": str(message.channel.id),
                        "user_id": str(message.author.id),
                    },
                )

                if resp.status_code == 200:
                    data = resp.json()
                    mode = data.get("mode", "unknown")

                    if mode == "instant":
                        # Run Python-side dispatch for instant tasks
                        await _dispatch_locally(message)
                    # For deep mode, Worker already sent "🤔 Thinking..."
                    # QStash callback will invoke the Brain endpoint
                else:
                    logger.warning(f"Worker returned {resp.status_code}: {resp.text}")

        except httpx.TimeoutException:
            await message.channel.send("⏳ Processing your request...")
            logger.info("Worker timeout — QStash will handle async delivery")

        except Exception as e:
            logger.error(f"Message handler error: {e}")
            await send_ghost_alert(
                alert_type="MESSAGE_HANDLER_ERROR",
                context={"error": str(e), "message": message.content[:200]},
            )


async def _dispatch_locally(message: discord.Message) -> None:
    """
    Run Python-side TaskDispatcher for instant-mode tasks.
    Imports lazily to avoid circular dependencies.
    """
    try:
        from packages.brain.task_dispatcher import TaskDispatcher
        from packages.infrastructure.redis_client import UltronRedis
        from packages.infrastructure.zilliz_client import ZillizPool
        from packages.brain.key_rotation.pool import KeyPool

        redis_url = os.getenv("UPSTASH_REDIS_URL", "")
        redis_token = os.getenv("UPSTASH_REDIS_TOKEN", "")

        if not redis_url or not redis_token:
            logger.warning("Redis not configured — skipping local dispatch")
            return

        redis = UltronRedis(url=redis_url, token=redis_token)
        zilliz = ZillizPool()
        key_pool = KeyPool(redis)
        dispatcher = TaskDispatcher(
            key_pool=key_pool, redis=redis, zilliz=zilliz
        )

        result = await dispatcher.dispatch({
            "message": message.content,
            "channel_id": str(message.channel.id),
            "user_id": str(message.author.id),
        })

        response_text = result.get("response", "")
        if response_text:
            # Split long responses for Discord's 2000 char limit
            for i in range(0, len(response_text), 1990):
                await message.channel.send(response_text[i:i + 1990])

        logger.info(
            f"Local dispatch: mode={result.get('mode')}, "
            f"type={result.get('task_type')}"
        )
    except Exception as e:
        logger.error(f"Local dispatch failed: {e}")
        await message.channel.send(
            "⚠️ I encountered an error processing your request. Please try again."
        )
