#!/usr/bin/env python3
"""
xiao-agent MCP Server
通过MCP协议提供浏览器控制工具，支持Windows Copilot等AI助手调用
"""

import asyncio
import json
import logging
from typing import Any

# MCP SDK
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent

# 本地模块
from mcp_tools import BrowserTools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建MCP服务器
app = Server("xiao-agent-browser")

# 浏览器工具实例
browser_tools = BrowserTools()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的浏览器控制工具"""
    return [
        Tool(
            name="browser_open_url",
            description="在浏览器中打开指定URL网页",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "要打开的网址，例如 https://www.baidu.com"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="browser_search",
            description="在搜索引擎中搜索内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "engine": {
                        "type": "string",
                        "description": "搜索引擎：baidu(百度)、google(谷歌)、bing(必应)",
                        "default": "baidu",
                        "enum": ["baidu", "google", "bing"]
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="browser_click",
            description="点击网页上的元素",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS选择器，例如 #button-id、.class-name、input[name='q']"
                    },
                    "description": {
                        "type": "string",
                        "description": "元素描述（可选），例如'搜索按钮'"
                    }
                },
                "required": ["selector"]
            }
        ),
        Tool(
            name="browser_input",
            description="在网页输入框中输入文本",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "输入框的CSS选择器"
                    },
                    "text": {
                        "type": "string",
                        "description": "要输入的文本内容"
                    }
                },
                "required": ["selector", "text"]
            }
        ),
        Tool(
            name="browser_scroll",
            description="滚动网页页面",
            inputSchema={
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "description": "滚动方向：up(向上)、down(向下)",
                        "enum": ["up", "down"],
                        "default": "down"
                    },
                    "amount": {
                        "type": "integer",
                        "description": "滚动距离（像素），默认500",
                        "default": 500
                    }
                }
            }
        ),
        Tool(
            name="browser_extract",
            description="提取网页中的数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "要提取元素的CSS选择器"
                    },
                    "attribute": {
                        "type": "string",
                        "description": "要提取的属性：text(文本)、html(HTML)、value(值)",
                        "default": "text",
                        "enum": ["text", "html", "value"]
                    }
                },
                "required": ["selector"]
            }
        ),
        Tool(
            name="browser_navigate",
            description="在当前标签页导航到新网址",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "要导航到的网址"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="browser_back",
            description="返回上一页",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="browser_forward",
            description="前进到下一页",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="browser_get_page_info",
            description="获取当前页面信息（URL、标题等）",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent | ImageContent]:
    """调用浏览器工具"""
    try:
        logger.info(f"调用工具: {name}, 参数: {arguments}")
        
        if name == "browser_open_url":
            result = await browser_tools.open_url(arguments["url"])
        elif name == "browser_search":
            result = await browser_tools.search(
                arguments["query"],
                arguments.get("engine", "baidu")
            )
        elif name == "browser_click":
            result = await browser_tools.click(
                arguments["selector"],
                arguments.get("description", "")
            )
        elif name == "browser_input":
            result = await browser_tools.input_text(
                arguments["selector"],
                arguments["text"]
            )
        elif name == "browser_scroll":
            result = await browser_tools.scroll(
                arguments.get("direction", "down"),
                arguments.get("amount", 500)
            )
        elif name == "browser_extract":
            result = await browser_tools.extract(
                arguments["selector"],
                arguments.get("attribute", "text")
            )
        elif name == "browser_navigate":
            result = await browser_tools.navigate(arguments["url"])
        elif name == "browser_back":
            result = await browser_tools.go_back()
        elif name == "browser_forward":
            result = await browser_tools.go_forward()
        elif name == "browser_get_page_info":
            result = await browser_tools.get_page_info()
        else:
            result = {"error": f"未知工具: {name}"}
        
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
    except Exception as e:
        logger.error(f"工具调用失败: {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]


async def main():
    """主函数"""
    logger.info("启动 xiao-agent MCP Server...")
    
    # 通过stdio传输运行服务器
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())