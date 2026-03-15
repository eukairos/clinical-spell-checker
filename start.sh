#!/usr/bin/env bash
# Clinical Spell Screener — Mac/Linux Launcher (Full Mode)
# Run: chmod +x start.sh && ./start.sh

cd "$(dirname "$0")"

echo ""
echo "============================================================"
echo "  Clinical Spell Screener"
echo "  Working directory: $(pwd)"
echo "============================================================"
echo ""

# ══════════════════════════════════════════════════════════════
# CONFIGURATION — Edit these if needed:
# ══════════════════════════════════════════════════════════════
CONDA_ENV="ollama_HF_py313"
# ══════════════════════════════════════════════════════════════

FOUND_CONDA=0
NO_MLM=0

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

if python -c "import torch" 2>/dev/null; then
    echo "  [OK] torch"
else
    echo "  [!] torch missing — installing..."
    pip install torch 2>/dev/null
    if python -c "import torch" 2>/dev/null; then
        echo "  [OK] torch installed"
    else
        echo "  [WARNING] torch install failed. Will use dictionary-only mode."
        NO_MLM=1
    fi
fi

if [ "$NO_MLM" -eq 0 ]; then
    if python -c "import transformers" 2>/dev/null; then
        echo "  [OK] transformers"
    else
        echo "  [!] transformers missing — installing..."
        pip install transformers 2>/dev/null
        if python -c "import transformers" 2>/dev/null; then
            echo "  [OK] transformers installed"
        else
            echo "  [WARNING] transformers install failed. Will use dictionary-only mode."
            NO_MLM=1
        fi
    fi
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
if [ "$NO_MLM" -eq 1 ]; then
    echo "  Starting dictionary-only mode..."
    echo "  Browser: http://localhost:8400"
    echo "  Press Ctrl+C to stop."
    echo ""
    python -m screener --no-model "$@"
else
    echo "  Starting with MLM backend..."
    echo "  First run downloads model ~500 MB — please be patient."
    echo "  Browser: http://localhost:8400"
    echo "  Press Ctrl+C to stop."
    echo ""
    python -m screener "$@"
fi
