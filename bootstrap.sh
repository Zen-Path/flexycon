#!/usr/bin/env bash
set -e

BOOTSTRAP_VENV=".venv"

# 1. Create minimal bootstrap venv
if [ ! -d "$BOOTSTRAP_VENV" ]; then
    echo "🐍 Creating bootstrap venv at $BOOTSTRAP_VENV"
    python3 -m venv "$BOOTSTRAP_VENV"
fi

# 2. Activate it
source "$BOOTSTRAP_VENV/bin/activate"

# 3. Install pip tools
echo "📦 Installing Hatch and Nox..."
pip install --upgrade pip
pip install hatch nox

# 4. Create Hatch environments
echo "📁 Initializing Hatch environments..."
hatch env create prod || true
hatch env create dev || true

# 5. Run full install logic via Nox
echo "🚀 Running nox -s install"
hatch run dev:nox -s install

echo "✅ Bootstrap complete. You can now run:"
echo "    source .venv/bin/activate"
echo "    hatch shell dev"
echo "    nox -s lint | format | test | ..."
