#!/usr/bin/env bash
# Clinical Spell Screener — Dictionary-Only Mode (no GPU required)
# Run: chmod +x start_lite.sh && ./start_lite.sh

cd "$(dirname "$0")"

echo ""
echo "============================================================"
echo "  Clinical Spell Screener — Dictionary-Only Mode"
echo "  Working directory: $(pwd)"
echo "============================================================"
echo ""

# ══════════════════════════════════════════════════════════════
# CONFIGURATION — Edit these if needed:
# ══════════════════════════════════════════════════════════════
CONDA_ENV="ollama_HF_py313"
# ══════════════════════════════════════════════════════════════

FOUND_CONDA=0

# ── Find conda ──
for P in "$HOME/anaconda3" "$HOME/miniconda3" "$HOME/Anaconda3" "$HOME/Miniconda3" "/opt/anaconda3" "/opt/miniconda3"; do
    if [ -f "$P/etc/profile.d/conda.sh" ]; then
        source "$P/etc/profile.d/conda.sh"
        FOUND_CONDA=1
        echo "  Conda found: $P"
        break
    fi
done

if [ "$FOUND_CONDA" -eq 0 ] && command -v conda &>/dev/null; then
    FOUND_CONDA=1
    echo "  Conda found: $(conda info --base)"
fi

if [ "$FOUND_CONDA" -eq 1 ]; then
    conda activate "$CONDA_ENV" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "  [WARNING] Could not activate '$CONDA_ENV'. Falling back to venv."
        FOUND_CONDA=0
    else
        echo "  Environment: $CONDA_ENV"
        python --version
        echo ""
    fi
fi

# ── Fall back to venv if no conda ──
if [ "$FOUND_CONDA" -eq 0 ]; then
    PYTHON=""
    if command -v python3 &>/dev/null; then
        PYTHON=python3
    elif command -v python &>/dev/null; then
        PYTHON=python
    fi

    if [ -z "$PYTHON" ]; then
        echo "  [ERROR] No Python found. Install Anaconda or Python 3.10+"
        exit 1
    fi

    echo "  Conda not found. Using Python venv."
    $PYTHON --version
    echo ""

    if [ ! -d ".venv" ]; then
        echo "  Creating virtual environment..."
        $PYTHON -m venv .venv
    fi
    source .venv/bin/activate
fi

# ── Check dependencies ──
echo "  Checking dependencies..."

if python -c "import fastapi" 2>/dev/null; then
    echo "  [OK] fastapi"
else
    echo "  [!] fastapi missing — installing..."
    pip install fastapi uvicorn
fi

if ! python -c "import screener" 2>/dev/null; then
    echo ""
    echo "  [ERROR] screener package not found."
    echo "  Contents of $(pwd):"
    ls -1
    echo ""
    exit 1
fi
echo "  [OK] screener"
echo ""

# ── Launch ──
echo "  Starting dictionary-only mode..."
echo "  Browser: http://localhost:8400"
echo "  Press Ctrl+C to stop."
echo ""
python -m screener --no-model "$@"
