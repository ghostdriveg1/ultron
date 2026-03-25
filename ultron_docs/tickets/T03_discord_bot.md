# T3 — Discord Bot Interface

## Context
Discord is Ghost's primary interface to Ultron. Works from any phone, anywhere in the world. The bot must receive messages, route them through the Worker, and send responses back. This is the most critical user-facing component.

**Dependencies:** T1, T2  
**Blocks:** T6 (needs Discord channel ID for responses)

## Files to Create

| File | Action | Purpose |
|---|---|---|
| `packages/interface/discord_bot.py` | Create | Bot gateway connection |
| `packages/interface/discord_sender.py` | Create | Message sending |
| `packages/interface/message_formatter.py` | Create | Format responses |

## Implementation Plan

### Step 1: Discord Application Setup (Manual, Ghost does once)
1. Go to discord.com/developers
2. Create application "Ultron"
3. Add Bot, copy token
4. Enable: MESSAGE CONTENT INTENT, GUILD MESSAGES INTENT
5. Invite to Ghost's server with message permissions
6. Copy channel ID
7. Paste bot token + channel ID into Ultron website settings

### Step 2: Discord Bot (discord_bot.py)
```python
import discord
from discord.ext import commands
import httpx
import asyncio

class UltronBot(commands.Bot):
    def __init__(self, cloudflare_worker_url: str):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.worker_url = cloudflare_worker_url
    
    async def on_ready(self):
        print(f'Ultron online as {self.user}')
    
    async def on_message(self, message: discord.Message):
        # Ignore messages from bots (including self)
        if message.author.bot:
            return
        
        # Only respond to DMs or specific channel
        if not isinstance(message.channel, discord.DMChannel):
            if message.channel.id != GHOST_CHANNEL_ID:
                return
        
        # Show typing indicator
        async with message.channel.typing():
            # Forward to Cloudflare Worker
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.worker_url}/discord",
                    json={
                        "content": message.content,
                        "author_id": str(message.author.id),
                        "channel_id": str(message.channel.id),
                        "message_id": str(message.id)
                    },
                    timeout=5.0
                )
```

### Step 3: Discord Sender (discord_sender.py)
```python
import discord
import asyncio
from typing import Optional

class DiscordSender:
    """Sends messages back to Ghost from anywhere in Ultron."""
    
    def __init__(self, bot_token: str, channel_id: int):
        self.token = bot_token
        self.channel_id = channel_id
    
    async def send(
        self, 
        content: str,
        embed: Optional[discord.Embed] = None,
        file: Optional[discord.File] = None
    ) -> None:
        """Send a message to Ghost's Discord channel."""
        # Handles: long messages (split at 2000 chars)
        # Handles: embeds for structured content
        # Handles: file attachments for documents
        
        if len(content) > 2000:
            # Split into multiple messages
            chunks = [content[i:i+1990] for i in range(0, len(content), 1990)]
            for chunk in chunks:
                await self._send_chunk(chunk)
        else:
            await self._send_chunk(content, embed, file)
    
    async def send_progress(
        self, 
        task_name: str, 
        progress: int,  # 0-100
        detail: str
    ) -> None:
        """Send a progress update with visual progress bar."""
        bar = "█" * (progress // 10) + "░" * (10 - progress // 10)
        await self.send(f"**{task_name}**\n{bar} {progress}%\n{detail}")
    
    async def send_error(self, error: str, task_id: str) -> None:
        """Send error notification requiring Ghost's attention."""
        embed = discord.Embed(
            title="🔴 Ultron Needs Help",
            description=error,
            color=discord.Color.red()
        )
        embed.add_field(name="Task ID", value=task_id)
        embed.add_field(name="Options", value="Reply: RETRY | SKIP | ABORT | [new instructions]")
        await self.send("", embed=embed)
```

### Step 4: Message Formatter (message_formatter.py)
```python
def format_response(content: str, response_type: str) -> str:
    """Format Ultron's responses for Discord."""
    
    if response_type == "CONVERSATIONAL":
        return content  # Plain text, no formatting
    
    elif response_type == "TASK_COMPLETE":
        return f"✅ **Done!**\n{content}"
    
    elif response_type == "TASK_STARTED":
        return f"🔄 **Starting...**\n{content}"
    
    elif response_type == "PROGRESS":
        return f"⚙️ {content}"
    
    elif response_type == "FILE_READY":
        return f"📎 **File ready:**\n{content}"
    
    elif response_type == "MORNING_BRIEFING":
        return f"☀️ **Good morning Ghost!**\n\n{content}"
```

## Acceptance Criteria
- [ ] Ghost messages Ultron on Discord → response within 12 seconds (conversational)
- [ ] Long responses (>2000 chars) → automatically split into multiple messages
- [ ] File attachments → sent as Discord file attachments
- [ ] Morning briefing sent at 8AM IST daily
- [ ] Error escalations show options: RETRY | SKIP | ABORT
- [ ] Bot ignores messages from other bots
- [ ] Bot only responds in Ghost's channel or DMs
- [ ] Typing indicator shows while processing

## Edge Cases
- Discord rate limit (5 msg/5s): queue messages and send with delay
- Message too long even when split: send as .txt file attachment
- Bot token expires: send email alert via Gmail API fallback
