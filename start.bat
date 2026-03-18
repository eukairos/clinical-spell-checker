@echo off
cd /d "%~dp0"
title Clinical Spell Screener

echo.
echo ============================================================
echo   Clinical Spell Screener (Full Mode - with AI assistance)
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

echo   Starting with MLM backend...
echo   First run installs dependencies and downloads model (~500 MB).
echo   Browser: http://localhost:8400
echo   Press Ctrl+C to stop.
echo.

uv run --extra mlm clinical-spell-screener %*

echo.
echo   Server stopped.
pause
