#!/usr/bin/env python3
"""
xiao-agent 主程序
小爱音箱语音控制 - 支持浏览器和Windows MCP控制
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.conversation import ConversationManager
from backend.ai_parser import AIParser
from backend.websocket_server import WebSocketServer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('system.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class XiaoAgent:
    """xiao-agent 主类"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self.load_config(config_path)
        self.conversation_manager = None
        self.ai_parser = None
        self.websocket_server = None
        self.running = False
        
    def load_config(self, config_path: str) -> dict:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"配置文件加载成功: {config_path}")
            return config
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            raise
    
    async def initialize(self):
        """初始化所有组件"""
        logger.info("正在初始化 xiao-agent...")
        
        # 1. AI解析器
        self.ai_parser = AIParser(self.config.get('openai_api', {}))
        logger.info("AI解析器初始化完成")
        
        # 2. WebSocket服务器
        ws_config = self.config.get('websocket', {'host': 'localhost', 'port': 8765})
        self.websocket_server = WebSocketServer(
            host=ws_config.get('host', 'localhost'),
            port=ws_config.get('port', 8765)
        )
        logger.info("WebSocket服务器初始化完成")
        
        # 3. 对话记录管理器
        self.conversation_manager = ConversationManager(
            xiaomi_config=self.config.get('xiaomi', {}),
            conversation_config=self.config.get('conversation', {}),
            ai_parser=self.ai_parser,
            websocket_server=self.websocket_server,
            mcp_callback=self.handle_mcp_command
        )
        logger.info("对话记录管理器初始化完成")
        
        # 4. 初始化MCP
        await self.init_mcp()
        
        logger.info("xiao-agent 初始化完成!")
    
    async def init_mcp(self):
        """初始化MCP服务器"""
        mcp_servers = self.config.get('mcp_servers', [])
        
        if not mcp_servers:
            logger.info("未配置MCP服务器，仅使用浏览器控制")
            return
        
        for server in mcp_servers:
            name = server.get('name')
            logger.info(f"MCP服务器配置: {name}")
        
        logger.info(f"已配置 {len(mcp_servers)} 个MCP服务器")
    
    async def handle_mcp_command(self, device_id: str, command: dict) -> dict:
        """处理MCP命令"""
        action = command.get('action')
        params = command.get('params', {})
        
        logger.info(f"执行命令: {action}, 参数: {params}")
        
        # 通过WebSocket发送到浏览器插件
        if self.websocket_server:
            await self.websocket_server.broadcast({
                "type": "command",
                "action": action,
                "params": params
            })
            logger.info(f"命令已发送到浏览器插件: {action}")
            return {"success": True, "message": f"已执行: {action}"}
        
        return {"success": False, "error": "无可用的执行方式"}
    
    async def start(self):
        """启动服务"""
        self.running = True
        logger.info("正在启动 xiao-agent...")
        
        ws_task = asyncio.create_task(self.websocket_server.start())
        conv_task = asyncio.create_task(self.conversation_manager.start_listening())
        
        logger.info("xiao-agent 启动完成!")
        logger.info("等待语音指令...")
        
        await asyncio.gather(ws_task, conv_task)
    
    async def stop(self):
        """停止服务"""
        self.running = False
        logger.info("xiao-agent 已停止")


async def main():
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