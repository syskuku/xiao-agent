#!/usr/bin/env python3
"""
对话记录管理器 - 基于xiaomusic原理
负责从小爱音箱获取语音指令，并转发给MCP处理
"""

import asyncio
import json
import time
import logging
from typing import Dict, Optional, Callable, Awaitable
from aiohttp import ClientSession, ClientTimeout

logger = logging.getLogger(__name__)

# 小米API端点
LATEST_ASK_API = "https://userprofile.mina.mi.com/device_profile/v2/conversation?source=dialogu&hardware={hardware}&timestamp={timestamp}&limit=2"


class ConversationManager:
    """对话记录管理器"""
    
    def __init__(
        self,
        xiaomi_config: dict,
        conversation_config: dict,
        ai_parser,
        websocket_server,
        mcp_callback: Optional[Callable[[str, dict], Awaitable[None]]] = None
    ):
        self.xiaomi_config = xiaomi_config
        self.conversation_config = conversation_config
        self.ai_parser = ai_parser
        self.websocket_server = websocket_server
        self.mcp_callback = mcp_callback  # MCP命令处理回调
        
        self.last_timestamp: Dict[str, int] = {}
        self.session: Optional[ClientSession] = None
        self.running = False
        self.devices = {}
    
    async def start_listening(self):
        """开始监听对话记录"""
        self.running = True
        logger.info("开始监听小爱音箱对话记录...")
        
        async with ClientSession() as session:
            self.session = session
            await self.discover_devices()
            
            while self.running:
                try:
                    if not self.conversation_config.get('enable_pull_ask', True):
                        await asyncio.sleep(5)
                        continue
                    
                    for device_id, device_info in self.devices.items():
                        await self.pull_conversation(device_id, device_info)
                    
                    interval = self.conversation_config.get('pull_interval', 2)
                    await asyncio.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"拉取对话记录出错: {e}")
                    await asyncio.sleep(5)
    
    async def discover_devices(self):
        """发现小爱音箱设备"""
        # 简化处理，实际需要从API获取
        self.devices = {
            "default_device": {
                "hardware": "L06A",
                "name": "小爱音箱"
            }
        }
        logger.info(f"发现 {len(self.devices)} 个设备")
    
    async def pull_conversation(self, device_id: str, device_info: dict):
        """拉取单个设备的对话记录"""
        try:
            hardware = device_info.get('hardware', 'L06A')
            
            if device_id not in self.last_timestamp:
                self.last_timestamp[device_id] = int(time.time() * 1000)
            
            url = LATEST_ASK_API.format(
                hardware=hardware,
                timestamp=str(int(time.time() * 1000))
            )
            
            cookies = {"deviceId": device_id}
            timeout = ClientTimeout(total=15)
            
            async with self.session.get(url, timeout=timeout, cookies=cookies) as response:
                if response.status == 200:
                    data = await response.json()
                    await self.process_conversation_data(device_id, data)
                    
        except Exception as e:
            logger.error(f"拉取设备 {device_id} 对话记录失败: {e}")
    
    async def process_conversation_data(self, device_id: str, data: dict):
        """处理对话记录数据"""
        try:
            if d := data.get("data"):
                records = json.loads(d).get("records")
                if not records:
                    return
                
                latest_record = records[0]
                timestamp = latest_record.get("time", 0)
                
                if timestamp > self.last_timestamp.get(device_id, 0):
                    self.last_timestamp[device_id] = timestamp
                    
                    query = latest_record.get("query", "").strip()
                    if query:
                        logger.info(f"🎤 收到语音指令: {query}")
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
                    await self.execute_action(device_id, action)
                    return
            
            # 2. 使用AI解析为MCP工具调用
            if self.conversation_config.get('enable_ai', True):
                logger.info(f"使用AI解析指令: {query}")
                
                # 获取所有可用工具描述
                tools_description = self.get_tools_description()
                
                ai_result = await self.ai_parser.parse_command(query, tools_description)
                
                if ai_result and ai_result.get("action"):
                    logger.info(f"AI解析成功: {ai_result}")
                    await self.execute_action(device_id, ai_result)
                else:
                    logger.warning(f"AI解析失败: {query}")
                    
        except Exception as e:
            logger.error(f"处理语音指令失败: {e}")
    
    def get_tools_description(self) -> str:
        """获取所有可用工具的描述"""
        try:
            from mcp_client import mcp_manager
            tools = mcp_manager.get_all_tools()
            
            desc = "可用工具列表：\n"
            for tool in tools:
                desc += f"- {tool['name']}: {tool.get('description', '无描述')}\n"
                if 'inputSchema' in tool:
                    props = tool['inputSchema'].get('properties', {})
                    if props:
                        desc += f"  参数: {list(props.keys())}\n"
            return desc
        except:
            return "无可用工具"
    
    def match_keyword_command(self, query: str) -> Optional[dict]:
        """关键词匹配（快速响应）"""
        query_lower = query.lower()
        
        # 浏览器相关
        if "打开" in query_lower and "百度" in query_lower:
            return {"action": "browser_open_url", "params": {"url": "https://www.baidu.com"}}
        elif "打开" in query_lower and "淘宝" in query_lower:
            return {"action": "browser_open_url", "params": {"url": "https://www.taobao.com"}}
        elif "搜索" in query_lower:
            import re
            match = re.search(r'搜索(.+)', query)
            if match:
                keyword = match.group(1).strip()
                return {"action": "browser_search", "params": {"query": keyword}}
        
        # 系统相关
        elif "打开记事本" in query_lower or "打开notepad" in query_lower:
            return {"action": "system_open_notepad", "params": {}}
        elif "打开计算器" in query_lower:
            return {"action": "system_open_calculator", "params": {}}
        
        return None
    
    async def execute_action(self, device_id: str, action: dict):
        """执行动作 - 优先调用MCP，失败则使用WebSocket"""
        try:
            # 1. 优先尝试MCP
            if self.mcp_callback:
                result = await self.mcp_callback(device_id, action)
                if result and result.get('success'):
                    logger.info(f"MCP执行成功: {action['action']}")
                    return
            
            # 2. 备选：通过WebSocket发送到浏览器插件
            if self.websocket_server:
                await self.websocket_server.broadcast(action)
                logger.info(f"已发送到浏览器插件: {action['action']}")
                
        except Exception as e:
            logger.error(f"执行动作失败: {e}")
    
    async def stop(self):
        """停止监听"""
        self.running = False
        logger.info("停止监听对话记录")