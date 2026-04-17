#!/usr/bin/env python3
"""
对话记录管理器 - 使用小米Cookie获取对话记录
"""

import asyncio
import json
import time
import logging
from typing import Dict, Optional, Callable, Awaitable
from aiohttp import ClientSession, ClientTimeout

logger = logging.getLogger(__name__)

LATEST_ASK_API = "https://userprofile.mina.mi.com/device_profile/v2/conversation?source=dialogu&hardware={hardware}&timestamp={timestamp}&limit=2"


class ConversationManager:
    """对话记录管理器"""
    
    def __init__(self, xiaomi_config: dict, conversation_config: dict, 
                 ai_parser, websocket_server, mcp_callback=None):
        self.xiaomi_config = xiaomi_config
        self.conversation_config = conversation_config
        self.ai_parser = ai_parser
        self.websocket_server = websocket_server
        self.mcp_callback = mcp_callback
        
        # 小米Cookie
        self.cookie = xiaomi_config.get('cookie', '')
        
        self.last_timestamp: Dict[str, int] = {}
        self.session: Optional[ClientSession] = None
        self.running = False
    
    async def start_listening(self):
        """开始监听对话记录"""
        self.running = True
        logger.info("开始监听小爱音箱对话记录...")
        
        if not self.cookie:
            logger.error("未配置小米Cookie！请在config.json中添加cookie字段")
            return
        
        async with ClientSession() as session:
            self.session = session
            
            while self.running:
                try:
                    await self.pull_conversation()
                    interval = self.conversation_config.get('pull_interval', 2)
                    await asyncio.sleep(interval)
                except Exception as e:
                    logger.error(f"拉取对话记录出错: {e}")
                    await asyncio.sleep(5)
    
    async def pull_conversation(self):
        """拉取对话记录"""
        hardware = "L06A"
        url = LATEST_ASK_API.format(
            hardware=hardware,
            timestamp=str(int(time.time() * 1000))
        )
        
        headers = {"Cookie": self.cookie}
        timeout = ClientTimeout(total=15)
        
        async with self.session.get(url, headers=headers, timeout=timeout) as response:
            if response.status == 200:
                data = await response.json()
                await self.process_conversation_data(data)
            else:
                logger.warning(f"请求失败，状态码: {response.status}")
    
    async def process_conversation_data(self, data: dict):
        """处理对话记录"""
        try:
            if d := data.get("data"):
                records = json.loads(d).get("records")
                if not records:
                    return
                
                latest_record = records[0]
                timestamp = latest_record.get("time", 0)
                
                if timestamp > self.last_timestamp.get("default", 0):
                    self.last_timestamp["default"] = timestamp
                    
                    query = latest_record.get("query", "").strip()
                    if query:
                        logger.info(f"🎤 收到语音指令: {query}")
                        await self.handle_voice_command(query)
                        
        except Exception as e:
            logger.error(f"处理对话数据失败: {e}")
    
    async def handle_voice_command(self, query: str):
        """处理语音指令"""
        try:
            # 1. 关键词匹配
            action = self.match_keyword_command(query)
            if action:
                logger.info(f"关键词匹配: {query} -> {action}")
                await self.execute_action(action)
                return
            
            # 2. AI解析
            if self.ai_parser:
                logger.info(f"AI解析: {query}")
                ai_result = await self.ai_parser.parse_command(query, "")
                if ai_result and ai_result.get("action"):
                    await self.execute_action(ai_result)
                    
        except Exception as e:
            logger.error(f"处理语音指令失败: {e}")
    
    def match_keyword_command(self, query: str) -> Optional[dict]:
        """关键词匹配"""
        q = query.lower()
        
        # 浏览器
        if "打开" in q and "百度" in q:
            return {"action": "open_url", "params": {"url": "https://www.baidu.com"}}
        if "打开" in q and "淘宝" in q:
            return {"action": "open_url", "params": {"url": "https://www.taobao.com"}}
        if "打开" in q and "京东" in q:
            return {"action": "open_url", "params": {"url": "https://www.jd.com"}}
        
        # 搜索
        if "搜索" in q:
            import re
            match = re.search(r'搜索(.+)', query)
            if match:
                return {"action": "search", "params": {"query": match.group(1).strip()}}
        
        # 系统
        if "打开记事本" in q:
            return {"action": "system_open_app", "params": {"app_name": "notepad"}}
        if "打开计算器" in q:
            return {"action": "system_open_app", "params": {"app_name": "calculator"}}
        if "截图" in q:
            return {"action": "system_screenshot", "params": {}}
        if "锁定" in q:
            return {"action": "system_lock", "params": {}}
        
        return None
    
    async def execute_action(self, action: dict):
        """执行动作"""
        try:
            # 通过WebSocket发送到Chrome扩展
            if self.websocket_server:
                await self.websocket_server.broadcast({
                    "type": "command",
                    "action": action.get("action"),
                    "params": action.get("params", {})
                })
                logger.info(f"命令已发送: {action.get('action')}")
                
        except Exception as e:
            logger.error(f"执行动作失败: {e}")
    
    async def stop(self):
        """停止监听"""
        self.running = False