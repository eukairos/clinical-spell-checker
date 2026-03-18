#!/usr/bin/env bash
# Clinical Spell Screener — Full Mode (with AI assistance)
cd "$(dirname "$0")"

echo ""
echo "============================================================"
echo "  Clinical Spell Screener (Full Mode - with AI assistance)"
echo "============================================================"
echo ""

# Check for uv
if ! command -v uv &>/dev/null; then
    echo "  uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "  Please restart your shell and run this script again."
    exit 0
fi

echo "  Starting with MLM backend..."
echo "  First run installs dependencies and downloads model (~500 MB)."
echo "  Browser: http://localhost:8400"
echo "  Press Ctrl+C to stop."
echo ""

uv run --extra mlm clinical-spell-screener "$@"
