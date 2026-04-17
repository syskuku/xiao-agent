@echo off
chcp 65001 >nul 2>&1

echo ==========================================
echo xiao-agent - Windows Deployment Script
echo ==========================================

echo [1/6] Checking Python...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ from https://www.python.org/downloads/
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
pip install -r backend\requirements.txt
echo Done.

echo [4/6] Creating config file...
if not exist "backend\config.json" (
    copy backend\config.example.json backend\config.json
    echo Please edit backend\config.json with your settings!
)

echo [5/6] Creating start.bat...
echo @echo off > start.bat
echo echo Starting xiao-agent... >> start.bat
echo cd backend >> start.bat
echo call venv\Scripts\activate.bat >> start.bat
echo python main.py >> start.bat
echo pause >> start.bat
echo Done.

echo [6/6] Creating stop.bat...
echo @echo off > stop.bat
echo echo Stopping xiao-agent... >> stop.bat
echo taskkill /F /IM python.exe >> stop.bat
echo echo Done. >> stop.bat
echo pause >> stop.bat
echo Done.

echo.
echo ============================================
echo Deployment Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Edit backend\config.json
echo 2. Run: start.bat
echo 3. Install Chrome extension from browser_extension folder
echo.
pause