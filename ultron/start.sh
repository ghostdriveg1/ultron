#!/bin/bash

echo "🚀 Ultron v3 — Starting in Codespaces..."

# ── Load .env ────────────────────────────────────────────────────────────────
if [ ! -f .env ]; then
  echo "❌ .env not found — run ./setup.sh first"
  exit 1
fi

# Export all non-comment lines from .env
set -a
# shellcheck disable=SC1091
source .env
set +a

# ── Re-inject Codespaces Brain URL (changes every session) ────────────────────
if [ -n "$CODESPACE_NAME" ]; then
  BRAIN_URL="https://${CODESPACE_NAME}-8000.app.github.dev"
  if grep -q "^CLAWCLOUD_BRAIN_URL=" .env; then
    sed -i "s|^CLAWCLOUD_BRAIN_URL=.*|CLAWCLOUD_BRAIN_URL=${BRAIN_URL}|" .env
  else
    echo "CLAWCLOUD_BRAIN_URL=${BRAIN_URL}" >> .env
  fi
  export CLAWCLOUD_BRAIN_URL="$BRAIN_URL"
  echo "🌐 Brain URL this session: ${BRAIN_URL}"
fi

# ── Health-check helper ───────────────────────────────────────────────────────
check() {
  local name="$1"
  local url="$2"
  echo "⏳ Waiting for ${name}..."
  for i in {1..20}; do
    if curl -sf "$url" > /dev/null 2>&1; then
      echo "✅ ${name} is up"
      return 0
    fi
    sleep 2
  done
  echo "❌ ${name} failed to start after 40s — check logs:"
  echo "   Brain:   tail -f /tmp/brain.log"
  echo "   Discord: tail -f /tmp/discord.log"
  exit 1
}

# ── Start Brain Agent ─────────────────────────────────────────────────────────
echo ""
echo "🧠 Starting Brain Agent (port 8000)..."
# main.py sits inside packages/brain/ — uvicorn is invoked from repo root
uvicorn packages.brain.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  > /tmp/brain.log 2>&1 &
BRAIN_PID=$!

check "Brain Agent" "http://localhost:8000/health"

# ── Start Discord Bot ─────────────────────────────────────────────────────────
echo ""
echo "🤖 Starting Discord Bot..."
python packages/interface/discord_bot.py > /tmp/discord.log 2>&1 &
DISCORD_PID=$!

sleep 3
if kill -0 "$DISCORD_PID" 2>/dev/null; then
  echo "✅ Discord Bot started (PID ${DISCORD_PID})"
else
  echo "❌ Discord Bot crashed — check /tmp/discord.log"
  exit 1
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "========================================================"
echo "✅ Ultron v3 Running"
echo ""
echo "  Brain Agent  : http://localhost:8000"
echo "  Brain URL    : ${CLAWCLOUD_BRAIN_URL:-<not in Codespaces>}"
echo ""
echo "  Logs:"
echo "    Brain   → tail -f /tmp/brain.log"
echo "    Discord → tail -f /tmp/discord.log"
echo ""
echo "  ⚠️  Remember: set port 8000 to PUBLIC in the Ports tab"
echo "     so Cloudflare Worker can reach it."
echo "========================================================"
echo ""

# Update Cloudflare reminder
if [ -n "$CLAWCLOUD_BRAIN_URL" ]; then
  echo "📋 Copy this into your Cloudflare Worker env vars:"
  echo "   BRAIN_AGENT_URL = ${CLAWCLOUD_BRAIN_URL}"
  echo ""
fi

echo "👀 Tailing live logs (Ctrl+C to stop all)..."
echo ""

# Kill both services cleanly on exit
trap "echo ''; echo 'Stopping...'; kill $BRAIN_PID $DISCORD_PID 2>/dev/null; echo '✅ Stopped.'" EXIT

# Show live logs from both services
tail -f /tmp/brain.log /tmp/discord.log
