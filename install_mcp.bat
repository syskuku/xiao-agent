@echo off

echo ==========================================
echo Install MCP for xiao-agent
echo ==========================================
echo.

cd /d "%~dp0.."
echo Directory: %CD%
echo.

if not exist "backend\venv" (
    echo [ERROR] Run setup.bat first!
    pause
    exit /b 1
)

echo Activating venv...
call backend\venv\Scripts\activate.bat
if errorlevel (
    echo [ERROR] Activate failed
    pause
    exit /b 1
)

echo.
echo Installing MCP...
pip install mcp
if errorlevel (
    echo [ERROR] Install failed
    pause
    exit /b 1
)

echo.
echo ============================================
echo SUCCESS! MCP installed!
echo ============================================
echo.
pause