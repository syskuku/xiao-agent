#!/usr/bin/env python3
"""
小爱音箱 + 兼容OpenAI格式的AI模型 + 浏览器控制系统 - 主程序
基于xiaomusic原理，实现语音指令控制浏览器
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from conversation import ConversationManager
from ai_parser import AIParser
from websocket_server import WebSocketServer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('system.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class BrowserControlSystem:
    """浏览器控制系统主类"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化系统"""
        self.config = self.load_config(config_path)
        self.conversation_manager = None
        self.ai_parser = None
        self.websocket_server = None
        self.running = False
        
    def load_config(self, config_path: str) -> dict:
        """加载配置文件"""
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
        try:
            # 初始化AI解析器
            self.ai_parser = AIParser(self.config['openai_api'])
            logger.info("AI解析器初始化完成")
            
            # 初始化WebSocket服务器
            self.websocket_server = WebSocketServer(
                host=self.config['websocket']['host'],
                port=self.config['websocket']['port']
            )
            logger.info("WebSocket服务器初始化完成")
            
            # 初始化对话记录管理器
            self.conversation_manager = ConversationManager(
                xiaomi_config=self.config['xiaomi'],
                conversation_config=self.config['conversation'],
                ai_parser=self.ai_parser,
                websocket_server=self.websocket_server
            )
            logger.info("对话记录管理器初始化完成")
            
        except Exception as e:
            logger.error(f"组件初始化失败: {e}")
            raise
    
    async def start(self):
        """启动系统"""
        try:
            self.running = True
            logger.info("正在启动浏览器控制系统...")
            
            # 启动WebSocket服务器
            ws_task = asyncio.create_task(self.websocket_server.start())
            
            # 启动对话记录监听
            conversation_task = asyncio.create_task(self.conversation_manager.start_listening())
            
            logger.info("系统启动完成，等待语音指令...")
            logger.info(f"WebSocket服务地址: ws://{self.config['websocket']['host']}:{self.config['websocket']['port']}")
            
            # 等待任务完成
            await asyncio.gather(ws_task, conversation_task)
            
        except Exception as e:
            logger.error(f"系统启动失败: {e}")
            raise
    
    async def stop(self):
        """停止系统"""
        self.running = False
        if self.conversation_manager:
            await self.conversation_manager.stop()
        if self.websocket_server:
            await self.websocket_server.stop()
        logger.info("系统已停止")

async def main():
    """主函数"""
    system = None
    try:
        # 创建系统实例
        system = BrowserControlSystem()
        
        # 初始化系统
        await system.initialize()
        
        # 启动系统
        await system.start()
        
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止系统...")
    except Exception as e:
        logger.error(f"系统运行出错: {e}")
    finally:
        if system:
            await system.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序已退出")