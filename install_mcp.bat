@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

echo ==========================================
echo xiao-agent - Install MCP Support
echo ==========================================

:: 检查虚拟环境
if not exist "backend\venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

:: 激活虚拟环境
echo Activating virtual environment...
call backend\venv\Scripts\activate.bat

:: 安装MCP
echo.
echo Installing MCP...
python -m pip install mcp

echo.
echo ============================================
echo MCP installed successfully!
echo ============================================
echo.
echo You can now use Windows control features:
echo - "Open Notepad"
echo - "Open Calculator" 
echo - "Lock computer"
echo - "Take screenshot"
echo.
echo Restart xiao-agent to apply changes.
echo.
pause