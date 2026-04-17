@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0\.."

echo ==========================================
echo xiao-agent - Windows Deployment
echo ==========================================
echo.

:: Check Python
echo [1/5] Checking Python...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Install from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Create venv
echo.
echo [2/5] Creating virtual environment...
if not exist "backend\venv" (
    python -m venv backend\venv
    echo Done.
) else (
    echo Already exists.
)

:: Install dependencies
echo.
echo [3/5] Installing dependencies...
call backend\venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
python -m pip install aiohttp websockets mcp -q
echo Done.

:: Create config
echo.
echo [4/5] Setting up config...
if not exist "backend\config.json" (
    copy backend\config.example.json backend\config.json >nul
    echo Config created. Please edit backend\config.json!
) else (
    echo Config exists.
)

:: Create start.bat
echo.
echo [5/5] Creating start.bat...
(
echo @echo off
echo cd /d "%%~dp0backend"
echo call venv\Scripts\activate.bat
echo python main.py
echo pause
) > start.bat
echo Done.

:: Create stop.bat
(
echo @echo off
echo taskkill /F /IM python.exe
echo pause
) > stop.bat

echo.
echo ==========================================
echo Deployment Complete!
echo.
echo Next steps:
echo 1. Edit backend\config.json
echo 2. Run start.bat
echo.
pause