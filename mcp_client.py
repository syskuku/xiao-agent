#!/usr/bin/env python3
"""
xiao-agent MCP Client
小爱音箱作为MCP客户端，可以调用任何MCP Server的工具
"""

import asyncio
import json
import logging
from typing import Any, Optional

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client

logger = logging.getLogger(__name__)


class MCPClientManager:
    """MCP客户端管理器 - 管理多个MCP Server连接"""
    
    def __init__(self):
        self.sessions: dict[str, ClientSession] = {}
        self.tools_cache: dict[str, list] = {}  # 工具缓存 server_name -> tools
    
    async def connect_stdio(self, name: str, command: str, args: list[str], cwd: str = None) -> bool:
        """通过stdio连接MCP Server"""
        try:
            server_params = StdioServerParameters(
                command=command,
                args=args,
                cwd=cwd
            )
            
            async with stdio_client(server_params) as (read_stream, write_stream):
                session = ClientSession(read_stream, write_stream)
                await session.initialize()
                
                self.sessions[name] = session
                
                # 获取工具列表并缓存
                tools_result = await session.list_tools()
                self.tools_cache[name] = [tool.model_dump() for tool in tools_result.tools]
                
                logger.info(f"已连接MCP Server '{name}'，获取到 {len(self.tools_cache[name])} 个工具")
                return True
                
        except Exception as e:
            logger.error(f"连接MCP Server '{name}' 失败: {e}")
            return False
    
    async def connect_http(self, name: str, url: str) -> bool:
        """通过HTTP连接MCP Server"""
        try:
            async with streamablehttp_client(url) as (read_stream, write_stream, _):
                session = ClientSession(read_stream, write_stream)
                await session.initialize()
                
                self.sessions[name] = session
                
                # 获取工具列表并缓存
                tools_result = await session.list_tools()
                self.tools_cache[name] = [tool.model_dump() for tool in tools_result.tools]
                
                logger.info(f"已连接MCP Server '{name}' (HTTP)，获取到 {len(self.tools_cache[name])} 个工具")
                return True
                
        except Exception as e:
            logger.error(f"连接MCP Server '{name}' (HTTP) 失败: {e}")
            return False
    
    def get_all_tools(self) -> list[dict]:
        """获取所有可用工具"""
        all_tools = []
        for server_name, tools in self.tools_cache.items():
            for tool in tools:
                tool["server"] = server_name
                all_tools.append(tool)
        return all_tools
    
    def find_tool(self, tool_name: str) -> Optional[tuple[str, dict]]:
        """查找工具"""
        for server_name, tools in self.tools_cache.items():
            for tool in tools:
                if tool["name"] == tool_name:
                    return server_name, tool
        return None
    
    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict:
        """调用工具"""
        result = self.find_tool(tool_name)
        if not result:
            return {"success": False, "error": f"未找到工具: {tool_name}"}
        
        server_name, tool_info = result
        session = self.sessions.get(server_name)
        
        if not session:
            return {"success": False, "error": f"MCP Server '{server_name}' 未连接"}
        
        try:
            result = await session.call_tool(tool_name, arguments)
            
            # 解析结果
            content = []
            for item in result.content:
                if hasattr(item, 'text'):
                    content.append(item.text)
                elif hasattr(item, 'data'):
                    content.append(str(item.data))
            
            return {
                "success": True,
                "server": server_name,
                "tool": tool_name,
                "content": content
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def disconnect_all(self):
        """断开所有连接"""
        for name, session in self.sessions.items():
            try:
                await session.close()
                logger.info(f"已断开MCP Server '{name}'")
            except:
                pass
        self.sessions.clear()
        self.tools_cache.clear()


# 全局MCP客户端管理器
mcp_manager = MCPClientManager()