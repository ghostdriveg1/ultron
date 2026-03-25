import asyncio
import os
from packages.interface.discord_sender import DiscordSender

class Watchdog:
    """Monitors log files for critical failures and alerts via Discord."""
    
    def __init__(self, discord: DiscordSender, logs_dir: str = "logs"):
        self.discord = discord
        self.logs_dir = logs_dir
        self._task = None
        self._last_positions = {}

    async def start(self):
        if self._task is None:
            self._task = asyncio.create_task(self._monitor_loop())

    async def _monitor_loop(self):
        while True:
            try:
                if not os.path.exists(self.logs_dir):
                    os.makedirs(self.logs_dir)
                    
                for filename in os.listdir(self.logs_dir):
                    if filename.endswith(".jsonl") or filename.endswith(".log"):
                        filepath = os.path.join(self.logs_dir, filename)
                        await self._check_file(filepath)
                        
            except Exception as e:
                print(f"Watchdog error: {e}")
                
            await asyncio.sleep(10) # Check every 10 seconds

    async def _check_file(self, filepath: str):
        if filepath not in self._last_positions:
            self._last_positions[filepath] = os.path.getsize(filepath) if os.path.exists(filepath) else 0
            return
            
        current_size = os.path.getsize(filepath)
        if current_size < self._last_positions[filepath]:
            # File rotated/truncated
            self._last_positions[filepath] = 0
            
        if current_size > self._last_positions[filepath]:
            with open(filepath, 'r', encoding='utf-8') as f:
                f.seek(self._last_positions[filepath])
                new_data = f.read()
                
            self._last_positions[filepath] = current_size
            
            # Look for CRITICAL or ERROR markers
            for line in new_data.splitlines():
                if "CRITICAL" in line or "Exception" in line:
                    alert_msg = f"🚨 Watchdog Alert ({os.path.basename(filepath)}): \n`{line[:200]}`"
                    await self.discord.send_message(alert_msg)
