#!/bin/bash
set -e

echo "🔧 Ultron v3 — Codespaces Setup"

echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt --quiet
echo "✅ Python deps installed"

echo ""
if [ ! -f .env ]; then
  cp .env.example .env
  echo "⚠️  .env created — fill in your real API keys now!"
else
  echo "✅ .env already exists"
fi

if [ -n "$CODESPACE_NAME" ]; then
  BRAIN_URL="https://${CODESPACE_NAME}-8000.app.github.dev"
  if grep -q "^CLAWCLOUD_BRAIN_URL=" .env; then
    sed -i "s|^CLAWCLOUD_BRAIN_URL=.*|CLAWCLOUD_BRAIN_URL=${BRAIN_URL}|" .env
  else
    echo "CLAWCLOUD_BRAIN_URL=${BRAIN_URL}" >> .env
  fi
  echo "✅ CLAWCLOUD_BRAIN_URL set to: ${BRAIN_URL}"
fi

echo ""
echo "✅ Setup complete. Run ./start.sh next."
