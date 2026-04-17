@echo off
chcp 65001 >nul 2>&1

echo ==========================================
echo xiao-agent - Install MCP Support
echo ==========================================
echo.

:: 获取脚本所在目录的上级目录（项目根目录）
set "PROJECT_DIR=%~dp0.."
cd /d "%PROJECT_DIR%"

echo Current directory: %CD%
echo.

:: 检查虚拟环境
if not exist "backend\venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run scripts\setup.bat first
    pause
    exit /b 1
)

:: 激活虚拟环境
echo [1/2] Activating virtual environment...
call "%CD%\backend\venv\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo Done.

:: 安装MCP
echo.
echo [2/2] Installing MCP...
python -m pip install mcp
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install MCP
    pause
    exit /b 1
)

echo.
echo ============================================
echo MCP installed successfully!
echo ============================================
echo.
echo Restart xiao-agent to use Windows control.
echo.
pause