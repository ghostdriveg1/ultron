#!/bin/bash

echo "🚀 Ultron v3 — Starting..."

if [ ! -f .env ]; then
  echo "❌ .env not found — run ./setup.sh first"
  exit 1
fi

set -a
source .env
set +a

if [ -n "$CODESPACE_NAME" ]; then
  BRAIN_URL="https://${CODESPACE_NAME}-8000.app.github.dev"
  sed -i "s|^CLAWCLOUD_BRAIN_URL=.*|CLAWCLOUD_BRAIN_URL=${BRAIN_URL}|" .env
  export CLAWCLOUD_BRAIN_URL="$BRAIN_URL"
  echo "🌐 Brain URL: ${BRAIN_URL}"
fi

check() {
  echo "⏳ Waiting for $1..."
  for i in {1..20}; do
    curl -sf "$2" > /dev/null 2>&1 && echo "✅ $1 is up" && return
    sleep 2
  done
  echo "❌ $1 failed — check logs"
  exit 1
}

echo ""
echo "🧠 Starting Brain Agent (port 8000)..."
uvicorn packages.brain.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/brain.log 2>&1 &
BRAIN_PID=$!
check "Brain Agent" "http://localhost:8000/health"

echo ""
echo "🤖 Starting Discord Bot..."
python packages/interface/discord_bot.py > /tmp/discord.log 2>&1 &
DISCORD_PID=$!
sleep 3
kill -0 "$DISCORD_PID" 2>/dev/null && echo "✅ Discord Bot running" || { echo "❌ Discord Bot crashed"; exit 1; }

echo ""
echo "========================================================"
echo "✅ Ultron v3 Running"
echo "  Brain Agent : http://localhost:8000"
echo "  Brain URL   : ${CLAWCLOUD_BRAIN_URL}"
echo "  Logs        : tail -f /tmp/brain.log /tmp/discord.log"
echo "  ⚠️  Set port 8000 to PUBLIC in the Ports tab!"
echo "========================================================"
echo ""
echo "📋 Set in Cloudflare Worker: BRAIN_AGENT_URL = ${CLAWCLOUD_BRAIN_URL}"
echo ""
echo "👀 Tailing logs (Ctrl+C to stop all)..."

trap "kill $BRAIN_PID $DISCORD_PID 2>/dev/null; echo 'Stopped.'" EXIT
tail -f /tmp/brain.log /tmp/discord.log
