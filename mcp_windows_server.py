#!/usr/bin/env python3
"""
Windows系统控制 MCP Server
通过小爱音箱控制Windows系统功能
"""

import asyncio
import json
import logging
import subprocess
import os

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Server("xiao-agent-windows")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有Windows控制工具"""
    return [
        Tool(
            name="system_open_app",
            description="打开Windows应用程序",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "应用名称：notepad(记事本)、calculator(计算器)、explorer(文件管理器)、cmd(CMD)、powershell"
                    }
                },
                "required": ["app_name"]
            }
        ),
        Tool(
            name="system_run_command",
            description="执行Windows命令",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "要执行的命令"
                    }
                },
                "required": ["command"]
            }
        ),
        Tool(
            name="system_volume",
            description="控制系统音量",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "操作：up(增大)、down(减小)、mute(静音)、set(设置)",
                        "enum": ["up", "down", "mute", "set"]
                    },
                    "value": {
                        "type": "integer",
                        "description": "音量值(0-100)，仅set操作需要"
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="system_lock",
            description="锁定电脑",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="system_shutdown",
            description="关机/重启电脑",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "操作：shutdown(关机)、restart(重启)、logout(注销)",
                        "enum": ["shutdown", "restart", "logout"]
                    },
                    "delay": {
                        "type": "integer",
                        "description": "延迟秒数，默认0",
                        "default": 0
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="system_screenshot",
            description="截取屏幕截图",
            inputSchema={
                "type": "object",
                "properties": {
                    "save_path": {
                        "type": "string",
                        "description": "保存路径，默认保存到桌面"
                    }
                }
            }
        ),
        Tool(
            name="system_open_url",
            description="用默认浏览器打开网址",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "要打开的网址"
                    }
                },
                "required": ["url"]
            }
        ),
    ]


# 应用名称映射
APP_MAP = {
    "notepad": "notepad.exe",
    "记事本": "notepad.exe",
    "calculator": "calc.exe",
    "计算器": "calc.exe",
    "explorer": "explorer.exe",
    "文件管理器": "explorer.exe",
    "cmd": "cmd.exe",
    "命令提示符": "cmd.exe",
    "powershell": "powershell.exe",
    "画图": "mspaint.exe",
    "paint": "mspaint.exe",
    "任务管理器": "taskmgr.exe",
    "控制面板": "control.exe",
}


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """调用工具"""
    try:
        if name == "system_open_app":
            app_name = arguments.get("app_name", "")
            exe = APP_MAP.get(app_name.lower(), app_name)
            subprocess.Popen(exe)
            result = f"已打开应用: {app_name}"
        
        elif name == "system_run_command":
            command = arguments.get("command", "")
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            result = f"命令输出:\n{result.stdout}\n{result.stderr}"
        
        elif name == "system_volume":
            action = arguments.get("action")
            # Windows音量控制需要特殊处理
            if action == "up":
                os.system("nircmd.exe changesysvolume 2000")
                result = "音量已增大"
            elif action == "down":
                os.system("nircmd.exe changesysvolume -2000")
                result = "音量已减小"
            elif action == "mute":
                os.system("nircmd.exe mutesysvolume 1")
                result = "已静音"
            else:
                result = "音量操作完成"
        
        elif name == "system_lock":
            os.system("rundll32.exe user32.dll,LockWorkStation")
            result = "电脑已锁定"
        
        elif name == "system_shutdown":
            action = arguments.get("action")
            delay = arguments.get("delay", 0)
            if action == "shutdown":
                os.system(f"shutdown /s /t {delay}")
                result = f"将在{delay}秒后关机"
            elif action == "restart":
                os.system(f"shutdown /r /t {delay}")
                result = f"将在{delay}秒后重启"
            elif action == "logout":
                os.system("shutdown /l")
                result = "已注销"
        
        elif name == "system_screenshot":
            # 使用PowerShell截图
            ps_script = '''
            Add-Type -AssemblyName System.Windows.Forms
            $screen = [System.Windows.Forms.Screen]::PrimaryScreen
            $bounds = $screen.Bounds
            $bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
            $desktop = [Environment]::GetFolderPath("Desktop")
            $bitmap.Save("$desktop\\screenshot.png", [System.Drawing.Imaging.ImageFormat]::Png)
            '''
            subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
            result = "截图已保存到桌面"
        
        elif name == "system_open_url":
            url = arguments.get("url", "")
            os.system(f'start "" "{url}"')
            result = f"已打开网址: {url}"
        
        else:
            result = f"未知工具: {name}"
        
        return [TextContent(type="text", text=json.dumps({"success": True, "result": result}, ensure_ascii=False))]
        
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))]


async def main():
    logger.info("启动 Windows MCP Server...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())