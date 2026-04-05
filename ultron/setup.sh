#!/bin/bash
set -e

echo "🔧 Ultron v3 — Codespaces Setup"

# Install Python deps
echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt --quiet
echo "✅ Python deps installed"

# Copy .env.example → .env if .env doesn't exist
echo ""
if [ ! -f .env ]; then
  cp .env.example .env
  echo "⚠️  .env created from .env.example — fill in your real API keys now!"
else
  echo "✅ .env already exists — skipping copy"
fi

# Auto-detect Codespaces URL and inject BRAIN_AGENT_URL
if [ -n "$CODESPACE_NAME" ]; then
  BRAIN_URL="https://${CODESPACE_NAME}-8000.app.github.dev"
  if grep -q "^CLAWCLOUD_BRAIN_URL=" .env; then
    sed -i "s|^CLAWCLOUD_BRAIN_URL=.*|CLAWCLOUD_BRAIN_URL=${BRAIN_URL}|" .env
  else
    echo "CLAWCLOUD_BRAIN_URL=${BRAIN_URL}" >> .env
  fi
  echo "✅ CLAWCLOUD_BRAIN_URL auto-set to: ${BRAIN_URL}"
else
  echo "ℹ️  Not in Codespaces — CLAWCLOUD_BRAIN_URL unchanged"
fi

echo ""
echo "=================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Open .env and fill in all API keys"
echo "  2. Run: ./start.sh"
echo "=================================="
