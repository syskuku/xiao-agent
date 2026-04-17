#!/usr/bin/env python3
"""
对话记录管理器 - 基于xiaomusic原理
负责从小爱音箱获取语音指令
"""

import asyncio
import json
import time
import logging
from typing import Dict, Optional, Callable
from aiohttp import ClientSession, ClientTimeout

logger = logging.getLogger(__name__)

# 小米API端点
LATEST_ASK_API = "https://userprofile.mina.mi.com/device_profile/v2/conversation?source=dialogu&hardware={hardware}&timestamp={timestamp}&limit=2"

class ConversationManager:
    """对话记录管理器"""
    
    def __init__(self, xiaomi_config: dict, conversation_config: dict, 
                 ai_parser, websocket_server):
        """初始化"""
        self.xiaomi_config = xiaomi_config
        self.conversation_config = conversation_config
        self.ai_parser = ai_parser
        self.websocket_server = websocket_server
        
        # 状态
        self.last_timestamp: Dict[str, int] = {}
        self.session: Optional[ClientSession] = None
        self.running = False
        
        # 设备信息
        self.devices = {}
        
    async def start_listening(self):
        """开始监听对话记录"""
        self.running = True
        logger.info("开始监听小爱音箱对话记录...")
        
        async with ClientSession() as session:
            self.session = session
            
            # 先获取设备列表
            await self.discover_devices()
            
            # 主循环
            while self.running:
                try:
                    if not self.conversation_config.get('enable_pull_ask', True):
                        await asyncio.sleep(5)
                        continue
                    
                    # 拉取所有设备的对话记录
                    for device_id, device_info in self.devices.items():
                        await self.pull_conversation(device_id, device_info)
                    
                    # 等待下一次拉取
                    interval = self.conversation_config.get('pull_interval', 2)
                    await asyncio.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"拉取对话记录出错: {e}")
                    await asyncio.sleep(5)
    
    async def discover_devices(self):
        """发现小爱音箱设备"""
        try:
            # 这里简化处理，实际需要调用小米API获取设备列表
            # 可以参考xiaomusic的device_manager.py
            logger.info("正在发现小爱音箱设备...")
            
            # 示例设备信息，实际需要从API获取
            self.devices = {
                "example_device_id": {
                    "hardware": "L06A",  # 小爱音箱型号
                    "name": "小爱音箱"
                }
            }
            
            logger.info(f"发现 {len(self.devices)} 个设备")
            
        except Exception as e:
            logger.error(f"发现设备失败: {e}")
    
    async def pull_conversation(self, device_id: str, device_info: dict):
        """拉取单个设备的对话记录"""
        try:
            hardware = device_info.get('hardware', 'L06A')
            
            # 初始化时间戳
            if device_id not in self.last_timestamp:
                self.last_timestamp[device_id] = int(time.time() * 1000)
            
            # 构建请求URL
            url = LATEST_ASK_API.format(
                hardware=hardware,
                timestamp=str(int(time.time() * 1000))
            )
            
            # 设置cookies
            cookies = {"deviceId": device_id}
            
            # 发送请求
            timeout = ClientTimeout(total=15)
            async with self.session.get(url, timeout=timeout, cookies=cookies) as response:
                if response.status == 200:
                    data = await response.json()
                    await self.process_conversation_data(device_id, data)
                else:
                    logger.warning(f"请求失败，状态码: {response.status}")
                    
        except Exception as e:
            logger.error(f"拉取设备 {device_id} 对话记录失败: {e}")
    
    async def process_conversation_data(self, device_id: str, data: dict):
        """处理对话记录数据"""
        try:
            if d := data.get("data"):
                records = json.loads(d).get("records")
                if not records:
                    return
                
                # 获取最新记录
                latest_record = records[0]
                timestamp = latest_record.get("time", 0)
                
                # 检查是否是新记录
                if timestamp > self.last_timestamp.get(device_id, 0):
                    self.last_timestamp[device_id] = timestamp
                    
                    # 提取用户指令
                    query = latest_record.get("query", "").strip()
                    if query:
                        logger.info(f"收到语音指令: {query}")
                        
                        # 处理指令
                        await self.handle_voice_command(device_id, query)
                        
        except Exception as e:
            logger.error(f"处理对话数据失败: {e}")
    
    async def handle_voice_command(self, device_id: str, query: str):
        """处理语音指令"""
        try:
            # 1. 先尝试关键词匹配（快速响应）
            if self.conversation_config.get('enable_keyword_fallback', True):
                action = self.match_keyword_command(query)
                if action:
                    logger.info(f"关键词匹配成功: {query} -> {action}")
                    await self.execute_action(action)
                    return
            
            # 2. 使用AI解析
            if self.conversation_config.get('enable_ai', True):
                logger.info(f"使用AI解析指令: {query}")
                ai_result = await self.ai_parser.parse_command(query)
                
                if ai_result and ai_result.get("action"):
                    logger.info(f"AI解析成功: {ai_result}")
                    await self.execute_action(ai_result)
                else:
                    logger.warning(f"AI解析失败或无有效指令: {query}")
            
        except Exception as e:
            logger.error(f"处理语音指令失败: {e}")
    
    def match_keyword_command(self, query: str) -> Optional[dict]:
        """关键词匹配（快速响应）"""
        query_lower = query.lower()
        
        # 简单的关键词匹配
        if "打开" in query_lower and "百度" in query_lower:
            return {"action": "open_url", "params": {"url": "https://www.baidu.com"}}
        elif "打开" in query_lower and "淘宝" in query_lower:
            return {"action": "open_url", "params": {"url": "https://www.taobao.com"}}
        elif "打开" in query_lower and "京东" in query_lower:
            return {"action": "open_url", "params": {"url": "https://www.jd.com"}}
        elif "搜索" in query_lower:
            # 提取搜索关键词
            import re
            match = re.search(r'搜索(.+)', query)
            if match:
                keyword = match.group(1).strip()
                return {"action": "search", "params": {"keyword": keyword}}
        
        return None
    
    async def execute_action(self, action: dict):
        """执行动作"""
        try:
            # 通过WebSocket发送到浏览器插件
            await self.websocket_server.broadcast(action)
            logger.info(f"已发送动作到浏览器插件: {action}")
            
        except Exception as e:
            logger.error(f"执行动作失败: {e}")
    
    async def stop(self):
        """停止监听"""
        self.running = False
        logger.info("停止监听对话记录")