@echo off
echo ============================================================
echo FREE FIRE TOKEN GENERATOR - BATCH MODE
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from python.org
    pause
    exit /b 1
)

echo [1/3] Checking dependencies...
pip show requests >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo [2/3] Generating tokens from test_credentials.txt...
python token_gen.py --batch

echo.
echo [3/3] Testing generated tokens...
python test_token.py

echo.
echo ============================================================
echo COMPLETE! Check generated_tokens.json for your tokens
echo ============================================================
pause
