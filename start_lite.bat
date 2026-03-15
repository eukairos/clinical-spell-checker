@echo off
cd /d "%~dp0"
title Clinical Spell Screener (Lightweight)
echo.
echo ============================================================
echo   Clinical Spell Screener — Dictionary-Only Mode
echo   (No GPU or PyTorch required)
echo ============================================================
echo   Working directory: %cd%
echo.

REM ── Find conda ──
set "CONDA_ENV=ollama_HF_py313"
set "FOUND_CONDA=0"

if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
    set "CONDA_PATH=%USERPROFILE%\anaconda3"
    set "FOUND_CONDA=1"
)
if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" (
    set "CONDA_PATH=%USERPROFILE%\miniconda3"
    set "FOUND_CONDA=1"
)
if exist "C:\ProgramData\anaconda3\Scripts\activate.bat" (
    set "CONDA_PATH=C:\ProgramData\anaconda3"
    set "FOUND_CONDA=1"
)
if exist "C:\ProgramData\miniconda3\Scripts\activate.bat" (
    set "CONDA_PATH=C:\ProgramData\miniconda3"
    set "FOUND_CONDA=1"
)

if "%FOUND_CONDA%"=="1" (
    echo   Conda found: %CONDA_PATH%
    call "%CONDA_PATH%\Scripts\activate.bat" "%CONDA_PATH%"
    call conda activate %CONDA_ENV%
    echo   Environment: %CONDA_ENV%
    python --version
    echo.
    goto :check_deps
)

REM ── No conda — try plain Python ──
echo   Conda not found. Trying plain Python...
where python >nul 2>&1
if errorlevel 1 (
    where py >nul 2>&1
    if errorlevel 1 (
        echo.
        echo   [ERROR] No Python found. Install Anaconda or Python 3.10+
        echo.
        pause
        exit /b 1
    )
)
if not exist ".venv\Scripts\activate.bat" (
    echo   Creating virtual environment...
    python -m venv .venv
)
call .venv\Scripts\activate.bat

:check_deps
echo   Checking dependencies...

python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo   [!] fastapi missing — installing...
    pip install fastapi uvicorn
    if errorlevel 1 (echo [ERROR] pip install failed. & pause & exit /b 1)
) else (
    echo   [OK] fastapi
)

python -c "import screener" >nul 2>&1
if errorlevel 1 (
    echo.
    echo   [ERROR] screener package not found.
    echo   Contents of %cd%:
    dir /b
    echo.
    pause
    exit /b 1
)
echo   [OK] screener
echo.

REM ── Start ──
echo   Starting dictionary-only mode...
echo   Browser: http://localhost:8400
echo   Press Ctrl+C to stop.
echo.
python -m screener --no-model

echo.
echo   Server stopped.
pause
