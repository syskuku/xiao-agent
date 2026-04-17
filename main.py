#!/usr/bin/env python3
"""
xiao-agent 主程序
小爱音箱 → AI解析 → MCP工具调用 → 控制各种设备/软件
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from backend.conversation import ConversationManager
from backend.ai_parser import AIParser
from backend.websocket_server import WebSocketServer
from mcp_client import mcp_manager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class XiaoAgent:
    """xiao-agent 主类 - 小爱音箱智能控制中心"""
    
    def __init__(self, config_path: str = "backend/config.json"):
        self.config = self.load_config(config_path)
        self.ai_parser = None
        self.conversation_manager = None
        self.websocket_server = None
        self.running = False
    
    def load_config(self, config_path: str) -> dict:
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            raise
    
    async def initialize(self):
        """初始化所有组件"""
        logger.info("正在初始化 xiao-agent...")
        
        # 1. 初始化AI解析器
        self.ai_parser = AIParser(self.config.get('openai_api', {}))
        logger.info("AI解析器初始化完成")
        
        # 2. 初始化WebSocket服务器（用于浏览器插件）
        ws_config = self.config.get('websocket', {})
        self.websocket_server = WebSocketServer(
            host=ws_config.get('host', 'localhost'),
            port=ws_config.get('port', 8765)
        )
        logger.info("WebSocket服务器初始化完成")
        
        # 3. 初始化对话记录管理器
        self.conversation_manager = ConversationManager(
            xiaomi_config=self.config.get('xiaomi', {}),
            conversation_config=self.config.get('conversation', {}),
            ai_parser=self.ai_parser,
            websocket_server=self.websocket_server,
            mcp_callback=self.handle_mcp_command
        )
        logger.info("对话记录管理器初始化完成")
        
        # 4. 连接MCP服务器
        await self.connect_mcp_servers()
        
        logger.info("xiao-agent 初始化完成!")
    
    async def connect_mcp_servers(self):
        """连接配置的MCP服务器"""
        mcp_servers = self.config.get('mcp_servers', [])
        
        if not mcp_servers:
            logger.info("未配置MCP服务器，使用内置浏览器控制功能")
            return
        
        for server_config in mcp_servers:
            name = server_config.get('name')
            server_type = server_config.get('type', 'stdio')
            
            if server_type == 'stdio':
                command = server_config.get('command')
                args = server_config.get('args', [])
                cwd = server_config.get('cwd')
                
                success = await mcp_manager.connect_stdio(name, command, args, cwd)
                if success:
                    logger.info(f"MCP服务器 '{name}' 连接成功")
                else:
                    logger.warning(f"MCP服务器 '{name}' 连接失败")
            
            elif server_type == 'http':
                url = server_config.get('url')
                success = await mcp_manager.connect_http(name, url)
                if success:
                    logger.info(f"MCP服务器 '{name}' (HTTP) 连接成功")
        
        # 显示所有可用工具
        all_tools = mcp_manager.get_all_tools()
        logger.info(f"当前可用工具总数: {len(all_tools)}")
        for tool in all_tools:
            logger.info(f"  - {tool['name']}: {tool.get('description', '无描述')}")
    
    async def handle_mcp_command(self, did: str, command: dict):
        """处理MCP命令"""
        action = command.get('action')
        params = command.get('params', {})
        
        logger.info(f"处理命令: {action}, 参数: {params}")
        
        # 查找对应的MCP工具
        result = await mcp_manager.call_tool(action, params)
        
        if result.get('success'):
            logger.info(f"工具调用成功: {result}")
        else:
            logger.warning(f"工具调用失败: {result}")
        
        # 通过WebSocket发送结果到浏览器插件（如果需要）
        if self.websocket_server:
            await self.websocket_server.broadcast({
                "type": "mcp_result",
                "action": action,
                "result": result
            })
        
        return result
    
    async def start(self):
        """启动服务"""
        self.running = True
        logger.info("正在启动 xiao-agent...")
        
        # 启动WebSocket服务器
        ws_task = asyncio.create_task(self.websocket_server.start())
        
        # 启动对话记录监听
        conv_task = asyncio.create_task(self.conversation_manager.start_listening())
        
        logger.info("✅ xiao-agent 启动完成!")
        logger.info("🎤 等待小爱音箱语音指令...")
        logger.info("🔌 MCP工具已就绪")
        
        await asyncio.gather(ws_task, conv_task)
    
    async def stop(self):
        """停止服务"""
        self.running = False
        await mcp_manager.disconnect_all()
        logger.info("xiao-agent 已停止")


async def main():
    """主函数"""
    agent = None
    try:
        agent = XiaoAgent()
        await agent.initialize()
        await agent.start()
    except KeyboardInterrupt:
        logger.info("收到中断信号")
    except Exception as e:
        logger.error(f"启动失败: {e}")
    finally:
        if agent:
            await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())