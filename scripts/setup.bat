@echo off
chcp 65001 >nul 2>&1

echo ==========================================
echo xiao-agent - Windows Deployment Script
echo ==========================================

cd /d "%~dp0\.."

echo [1/6] Checking Python...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)

echo [2/6] Creating virtual environment...
if not exist "backend\venv" (
    python -m venv backend\venv
)
echo Done.

echo [3/6] Installing dependencies...
call backend\venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install aiohttp websockets mcp
echo Done.

echo [4/6] Creating config file...
if not exist "backend\config.json" (
    copy backend\config.example.json backend\config.json
    echo Please edit backend\config.json!
)

echo [5/6] Creating start.bat...
(
echo @echo off
echo cd /d "%%~dp0backend"
echo call venv\Scripts\activate.bat
echo python main.py
echo pause
) > start.bat
echo Done.

echo [6/6] Creating stop.bat...
(
echo @echo off
echo taskkill /F /IM python.exe
echo pause
) > stop.bat
echo Done.

echo.
echo ============================================
echo Deployment Complete!
echo.
echo Next steps:
echo 1. Edit backend\config.json
echo 2. Run start.bat
echo.
pause