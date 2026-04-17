@echo off
cd /d "%~dp0.."
call backend\venv\Scripts\activate.bat
pip install mcp
pause