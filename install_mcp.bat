@echo off

echo ==========================================
echo Install MCP for xiao-agent
echo ==========================================
echo.

:: 自动识别路径
echo [1] Detecting path...
echo Current directory: %CD%
echo Script location: %~dp0

:: 切换到项目根目录
cd /d "%~dp0"
cd ..
set "PROJECT_DIR=%CD%"
echo Project directory: %PROJECT_DIR%
echo.

:: 检查backend目录
if not exist "backend" (
    echo [ERROR] Cannot find backend folder!
    echo Please make sure you are in the correct project directory.
    echo.
    echo Expected structure:
    echo   xiao-agent/
    echo     ├── backend/
    echo     ├── scripts/
    echo     └── install_mcp.bat
    echo.
    pause
    exit /b 1
)

:: 检查虚拟环境
if not exist "backend\venv" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run setup.bat first:
    echo   1. Open CMD
    echo   2. Go to: %PROJECT_DIR%\scripts
    echo   3. Run: setup.bat
    echo.
    pause
    exit /b 1
)

:: 检查activate.bat
if not exist "backend\venv\Scripts\activate.bat" (
    echo [ERROR] activate.bat not found!
    echo Virtual environment might be corrupted.
    echo Please delete backend\venv and run setup.bat again.
    pause
    exit /b 1
)

echo [2] Activating virtual environment...
call "%PROJECT_DIR%\backend\venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)
echo Done.
echo.

echo [3] Installing MCP...
pip install mcp
if errorlevel 1 (
    echo [ERROR] Failed to install MCP!
    echo Check your internet connection.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo SUCCESS! MCP installed!
echo ==========================================
echo.
echo Now you can restart xiao-agent:
echo   1. Close current window
echo   2. Run start.bat
echo.
pause