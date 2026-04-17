@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

echo ==========================================
echo xiao-agent - One-Click Start
echo ==========================================

:: 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 创建虚拟环境（如果不存在）
if not exist "backend\venv" (
    echo [1/4] Creating virtual environment...
    python -m venv backend\venv
)

:: 激活并安装依赖
echo [2/4] Installing dependencies...
call backend\venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
python -m pip install aiohttp websockets mcp -q

:: 创建配置文件（如果不存在）
if not exist "backend\config.json" (
    echo [3/4] Creating config file...
    copy backend\config.example.json backend\config.json >nul
    echo.
    echo ============================================
    echo Please edit backend\config.json first!
    echo Need: Xiaomi account, password, AI API key
    echo ============================================
    echo.
    notepad backend\config.json
    pause
) else (
    echo [3/4] Config file exists.
)

:: 启动服务
echo [4/4] Starting xiao-agent...
echo.
echo ============================================
echo xiao-agent is running!
echo Press Ctrl+C to stop
echo ============================================
echo.
cd backend
python main.py

pause