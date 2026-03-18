@echo off
cd /d "%~dp0"
title Clinical Spell Screener (Lightweight)

echo.
echo ============================================================
echo   Clinical Spell Screener (Dictionary-Only Mode)
echo   No GPU or PyTorch required
echo ============================================================
echo.

REM ── Check for uv ──
where uv >nul 2>&1
if errorlevel 1 (
    echo   uv not found. Installing...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo   Please restart this script after installation.
    pause
    exit /b 0
)

echo   Browser: http://localhost:8400
echo   Press Ctrl+C to stop.
echo.

uv run clinical-spell-screener --no-model %*

echo.
echo   Server stopped.
pause
