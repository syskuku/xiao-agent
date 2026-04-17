#!/usr/bin/env python3
"""
对话记录管理器 - 基于xiaomusic原理
负责从小爱音箱获取语音指令，并转发给MCP处理
支持TTS播报功能
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
        self.mcp_callback = mcp_callback
        
        self.last_timestamp: Dict[str, int] = {}
        self.session: Optional[ClientSession] = None
        self.running = False
        self.devices = {}
        
        # TTS配置
        self.tts_enabled = conversation_config.get('tts_enabled', True)
        self.tts_confirm = conversation_config.get('tts_confirm', '好的，正在处理')
        self.tts_success = conversation_config.get('tts_success', '已完成')
        self.tts_error = conversation_config.get('tts_error', '抱歉，执行失败')
    
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
            # TTS播报：收到指令
            if self.tts_enabled:
                await self.do_tts(device_id, self.tts_confirm)
            
            # 1. 先尝试关键词匹配
            if self.conversation_config.get('enable_keyword_fallback', True):
                action = self.match_keyword_command(query)
                if action:
                    logger.info(f"关键词匹配成功: {query} -> {action}")
                    result = await self.execute_action(device_id, action)
                    await self播报结果(device_id, result)
                    return
            
            # 2. 使用AI解析
            if self.conversation_config.get('enable_ai', True):
                logger.info(f"使用AI解析指令: {query}")
                
                tools_description = self.get_tools_description()
                ai_result = await self.ai_parser.parse_command(query, tools_description)
                
                if ai_result and ai_result.get("action"):
                    logger.info(f"AI解析成功: {ai_result}")
                    result = await self.execute_action(device_id, ai_result)
                    await self.播报结果(device_id, result)
                else:
                    logger.warning(f"AI解析失败: {query}")
                    if self.tts_enabled:
                        await self.do_tts(device_id, f"抱歉，无法理解指令：{query}")
                    
        except Exception as e:
            logger.error(f"处理语音指令失败: {e}")
            if self.tts_enabled:
                await self.do_tts(device_id, f"执行出错：{str(e)}")
    
    async def 播报结果(self, device_id: str, result: dict):
        """播报执行结果"""
        if not self.tts_enabled:
            return
        
        if result and result.get('success'):
            # 成功播报
            message = result.get('message', self.tts_success)
            await self.do_tts(device_id, f"{self.tts_success}，{message}")
        else:
            # 失败播报
            error = result.get('error', '未知错误') if result else '执行失败'
            await self.do_tts(device_id, f"{self.tts_error}，{error}")
    
    async def do_tts(self, device_id: str, text: str):
        """执行TTS播报 - 使用小米原生TTS"""
        if not text:
            return
        
        try:
            # 方式1: 使用小米MiNA服务（推荐）
            # 这里需要调用xiaomusic的TTS接口
            # 暂时记录日志，实际实现需要集成xiaomusic的MiNA服务
            logger.info(f"🔊 TTS播报: {text}")
            
            # TODO: 集成xiaomusic的MiNA服务
            # await self.mina_service.text_to_speech(device_id, text)
            
        except Exception as e:
            logger.error(f"TTS播报失败: {e}")
    
    def get_tools_description(self) -> str:
        """获取所有可用工具的描述"""
        try:
            from mcp_client import mcp_manager
            tools = mcp_manager.get_all_tools()
            
            desc = "可用工具列表：\n"
            for tool in tools:
                desc += f"- {tool['name']}: {tool.get('description', '无描述')}\n"
            return desc
        except:
            return "无可用工具"
    
    def match_keyword_command(self, query: str) -> Optional[dict]:
        """关键词匹配"""
        query_lower = query.lower()
        
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
        elif "打开记事本" in query_lower:
            return {"action": "system_open_app", "params": {"app_name": "notepad"}}
        elif "打开计算器" in query_lower:
            return {"action": "system_open_app", "params": {"app_name": "calculator"}}
        elif "截图" in query_lower:
            return {"action": "system_screenshot", "params": {}}
        elif "锁定" in query_lower:
            return {"action": "system_lock", "params": {}}
        
        return None
    
    async def execute_action(self, device_id: str, action: dict) -> dict:
        """执行动作"""
        try:
            # 优先尝试MCP
            if self.mcp_callback:
                result = await self.mcp_callback(device_id, action)
                if result and result.get('success'):
                    logger.info(f"MCP执行成功: {action['action']}")
                    return result
            
            # 备选：通过WebSocket发送到浏览器插件
            if self.websocket_server:
                await self.websocket_server.broadcast(action)
                logger.info(f"已发送到浏览器插件: {action['action']}")
                return {"success": True, "message": "已发送到浏览器"}
                
            return {"success": False, "error": "无可用的执行方式"}
                
        except Exception as e:
            logger.error(f"执行动作失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def stop(self):
        """停止监听"""
        self.running = False
        logger.info("停止监听对话记录")