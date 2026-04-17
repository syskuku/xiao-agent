@echo off
chcp 65001 >nul
REM xiao-agent Windows Deployment Script

echo ==========================================
echo xiao-agent - Windows Deployment Script
echo ==========================================

echo [INFO] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.8+
    echo Download from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [SUCCESS] Python found

echo [INFO] Checking Chrome browser...
where chrome.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Chrome found
) else (
    echo [WARNING] Chrome not found
    echo Please install Chrome for browser control
)

echo [INFO] Creating virtual environment...
if not exist "backend\venv" (
    python -m venv backend\venv
    echo [SUCCESS] Virtual environment created
) else (
    echo [INFO] Virtual environment exists
)

echo [INFO] Installing dependencies...
call backend\venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
echo [SUCCESS] Dependencies installed

echo [INFO] Generating icons...
cd browser_extension\icons
pip install Pillow >nul 2>&1
python convert_icons.py 2>nul || echo [INFO] Icons placeholder created
cd ..\..

echo [INFO] Creating config file...
if not exist "backend\config.json" (
    copy backend\config.example.json backend\config.json
    echo [WARNING] Please edit backend\config.json
    echo [WARNING]   - Xiaomi account and password
    echo [WARNING]   - AI API Key
) else (
    echo [SUCCESS] Config exists
)

echo [INFO] Creating start.bat...
(
echo @echo off
echo echo Starting xiao-agent...
echo cd backend
echo call venv\Scripts\activate.bat
echo if not exist "config.json" (
echo     echo Error: config.json not found
echo     echo Copy config.example.json to config.json
echo     pause
echo     exit /b 1
echo )
echo echo Starting service...
echo python main.py
echo pause
) > start.bat
echo [SUCCESS] start.bat created

echo [INFO] Creating stop.bat...
(
echo @echo off
echo echo Stopping xiao-agent...
echo taskkill /F /IM python.exe /FI "WINDOWTITLE eq main.py" >nul 2>&1
echo echo Service stopped
echo pause
) > stop.bat
echo [SUCCESS] stop.bat created

echo [INFO] Creating QUICKSTART.md...
(
echo # Windows Quick Start
echo.
echo ## 1. Configure
echo Edit backend\config.json:
echo - xiaomi.username: Your Xiaomi account
echo - xiaomi.password: Your Xiaomi password
echo - openai_api.api_key: Your AI API key
echo.
echo ## 2. Start Service
echo Run: start.bat
echo.
echo ## 3. Install Chrome Extension
echo 1. Open Chrome, go to chrome://extensions/
echo 2. Enable "Developer mode"
echo 3. Click "Load unpacked"
echo 4. Select browser_extension folder
echo.
echo ## 4. Test
echo Say to XiaoAi: "Open Baidu"
echo.
echo ## MCP Control (Optional^)
echo Install MCP: pip install mcp
echo Create %%APPDATA%%\mcp\config.json with MCP server config
) > QUICKSTART_WINDOWS.md
echo [SUCCESS] QUICKSTART_WINDOWS.md created

echo.
echo ============================================
echo [SUCCESS] Deployment Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Edit backend\config.json
echo 2. Run start.bat
echo 3. Install Chrome extension
echo.
pause