#!/usr/bin/env bash
# Clinical Spell Screener — Dictionary-Only Mode (no GPU required)
cd "$(dirname "$0")"

echo ""
echo "============================================================"
echo "  Clinical Spell Screener (Dictionary-Only Mode)"
echo "============================================================"
echo ""

# Check for uv
if ! command -v uv &>/dev/null; then
    echo "  uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "  Please restart your shell and run this script again."
    exit 0
fi

echo "  Browser: http://localhost:8400"
echo "  Press Ctrl+C to stop."
echo ""

uv run clinical-spell-screener --no-model "$@"
