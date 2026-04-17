#!/usr/bin/env python3
"""
浏览器控制工具 - 通过WebSocket连接Chrome插件执行浏览器操作
"""

import asyncio
import json
import logging
import websockets
from typing import Optional

logger = logging.getLogger(__name__)


class BrowserTools:
    """浏览器控制工具类"""
    
    def __init__(self, ws_host: str = "localhost", ws_port: int = 8765):
        self.ws_host = ws_host
        self.ws_port = ws_port
        self.ws_url = f"ws://{ws_host}:{ws_port}"
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
    
    async def _connect(self) -> bool:
        """连接到WebSocket服务器"""
        try:
            if self.websocket is None or self.websocket.closed:
                self.websocket = await websockets.connect(self.ws_url)
                logger.info(f"已连接到WebSocket服务器: {self.ws_url}")
            return True
        except Exception as e:
            logger.error(f"连接WebSocket失败: {e}")
            return False
    
    async def _send_command(self, command: dict) -> dict:
        """发送命令到浏览器插件"""
        if not await self._connect():
            return {"success": False, "error": "无法连接到浏览器插件服务"}
        
        try:
            await self.websocket.send(json.dumps(command))
            
            # 等待响应（带超时）
            response = await asyncio.wait_for(self.websocket.recv(), timeout=10)
            return json.loads(response)
        except asyncio.TimeoutError:
            return {"success": False, "error": "命令执行超时"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def open_url(self, url: str) -> dict:
        """打开网页"""
        return await self._send_command({
            "action": "open_url",
            "params": {"url": url}
        })
    
    async def search(self, query: str, engine: str = "baidu") -> dict:
        """搜索内容"""
        # 构建搜索URL
        search_urls = {
            "baidu": f"https://www.baidu.com/s?wd={query}",
            "google": f"https://www.google.com/search?q={query}",
            "bing": f"https://www.bing.com/search?q={query}"
        }
        url = search_urls.get(engine, search_urls["baidu"])
        return await self.open_url(url)
    
    async def click(self, selector: str, description: str = "") -> dict:
        """点击元素"""
        return await self._send_command({
            "action": "click",
            "params": {
                "selector": selector,
                "description": description
            }
        })
    
    async def input_text(self, selector: str, text: str) -> dict:
        """输入文本"""
        return await self._send_command({
            "action": "input",
            "params": {
                "selector": selector,
                "text": text
            }
        })
    
    async def scroll(self, direction: str = "down", amount: int = 500) -> dict:
        """滚动页面"""
        return await self._send_command({
            "action": "scroll",
            "params": {
                "direction": direction,
                "amount": amount
            }
        })
    
    async def extract(self, selector: str, attribute: str = "text") -> dict:
        """提取数据"""
        return await self._send_command({
            "action": "extract",
            "params": {
                "selector": selector,
                "attribute": attribute
            }
        })
    
    async def navigate(self, url: str) -> dict:
        """导航到新页面"""
        return await self._send_command({
            "action": "navigate",
            "params": {"url": url}
        })
    
    async def go_back(self) -> dict:
        """返回上一页"""
        return await self._send_command({
            "action": "back",
            "params": {}
        })
    
    async def go_forward(self) -> dict:
        """前进到下一页"""
        return await self._send_command({
            "action": "forward",
            "params": {}
        })
    
    async def get_page_info(self) -> dict:
        """获取当前页面信息"""
        return await self._send_command({
            "action": "get_page_info",
            "params": {}
        })
    
    async def close(self):
        """关闭连接"""
        if self.websocket and not self.websocket.closed:
            await self.websocket.close()
            logger.info("WebSocket连接已关闭")