#!/usr/bin/env bash
# ─── Ultron v3 — Development Setup Script ─────────────────────
# One-command setup: checks prerequisites, installs deps, starts dev env.
set -euo pipefail

echo "╔══════════════════════════════════════════════╗"
echo "║     ULTRON v3 — Development Environment      ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ─── Check Python 3.11+ ──────────────────────────────────────
echo "→ Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>/dev/null | grep -oP '\d+\.\d+' || echo "0.0")
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    echo "  ✗ Python 3.11+ required (found $PYTHON_VERSION)"
    echo "  Install: https://www.python.org/downloads/"
    exit 1
fi
echo "  ✓ Python $PYTHON_VERSION"

# ─── Check Node.js ────────────────────────────────────────────
echo "→ Checking Node.js version..."
NODE_VERSION=$(node --version 2>/dev/null || echo "none")
if [ "$NODE_VERSION" = "none" ]; then
    echo "  ✗ Node.js not found"
    echo "  Install: https://nodejs.org/"
    exit 1
fi
echo "  ✓ Node.js $NODE_VERSION"

# ─── Install Python dependencies ─────────────────────────────
echo "→ Installing Python dependencies..."
pip install -r requirements.txt --quiet
echo "  ✓ Python packages installed"

# ─── Install Node.js dependencies ────────────────────────────
echo "→ Installing Node.js dependencies..."
npm install --silent
echo "  ✓ Node.js packages installed"

# ─── Copy .env if not exists ─────────────────────────────────
if [ ! -f .env ]; then
    echo "→ Creating .env from .env.example..."
    cp .env.example .env
    echo "  ✓ .env created — fill in your API keys"
else
    echo "  ✓ .env already exists"
fi

# ─── Start Redis via Docker Compose ──────────────────────────
echo "→ Starting Redis..."
docker-compose up -d redis 2>/dev/null || echo "  ⚠ Docker not available — skip Redis (use Upstash instead)"
echo ""

echo "╔══════════════════════════════════════════════╗"
echo "║         Setup complete! Next steps:          ║"
echo "║  1. Fill in API keys in .env                 ║"
echo "║  2. npm run dev:worker  (CF Worker)          ║"
echo "║  3. npm run dev:website (React dashboard)    ║"
echo "║  4. python packages/interface/discord_bot.py ║"
echo "╚══════════════════════════════════════════════╝"
