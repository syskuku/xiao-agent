#!/usr/bin/env python3
"""
WebSocket服务器 - 与浏览器插件通信
"""

import asyncio
import json
import logging
import websockets
from typing import Dict, Set, Optional
from websockets.server import serve

logger = logging.getLogger(__name__)

class WebSocketServer:
    """WebSocket服务器"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        """初始化WebSocket服务器"""
        self.host = host
        self.port = port
        self.connected_clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.server = None
        
    async def handler(self, websocket, path):
        """处理WebSocket连接"""
        client_id = None
        try:
            # 等待客户端注册消息
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    # 处理注册消息
                    if data.get("type") == "register":
                        client_id = data.get("client_id", f"client_{len(self.connected_clients)}")
                        self.connected_clients[client_id] = websocket
                        logger.info(f"客户端已注册: {client_id}")
                        
                        # 发送注册确认
                        await websocket.send(json.dumps({
                            "type": "registered",
                            "client_id": client_id,
                            "status": "success"
                        }))
                        
                    # 处理心跳消息
                    elif data.get("type") == "heartbeat":
                        await websocket.send(json.dumps({
                            "type": "heartbeat_response",
                            "timestamp": data.get("timestamp")
                        }))
                        
                    # 处理执行结果反馈
                    elif data.get("type") == "execution_result":
                        logger.info(f"收到来自 {client_id} 的执行结果: {data}")
                        
                    # 处理错误反馈
                    elif data.get("type") == "error":
                        logger.error(f"收到来自 {client_id} 的错误: {data}")
                        
                except json.JSONDecodeError:
                    logger.warning(f"收到无效JSON消息: {message}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"客户端连接关闭: {client_id}")
        except Exception as e:
            logger.error(f"处理客户端消息出错: {e}")
        finally:
            # 清理连接
            if client_id and client_id in self.connected_clients:
                del self.connected_clients[client_id]
                logger.info(f"客户端已断开: {client_id}")
    
    async def start(self):
        """启动WebSocket服务器"""
        try:
            self.server = await serve(self.handler, self.host, self.port)
            logger.info(f"WebSocket服务器已启动: ws://{self.host}:{self.port}")
            
            # 保持服务器运行
            await asyncio.Future()  # run forever
            
        except Exception as e:
            logger.error(f"WebSocket服务器启动失败: {e}")
            raise
    
    async def stop(self):
        """停止WebSocket服务器"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("WebSocket服务器已停止")
    
    async def broadcast(self, message: dict):
        """广播消息到所有连接的客户端"""
        if not self.connected_clients:
            logger.warning("没有连接的客户端，无法广播消息")
            return
        
        message_json = json.dumps(message)
        disconnected_clients = []
        
        for client_id, websocket in self.connected_clients.items():
            try:
                await websocket.send(message_json)
                logger.debug(f"已发送消息到客户端 {client_id}")
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(client_id)
            except Exception as e:
                logger.error(f"发送消息到客户端 {client_id} 失败: {e}")
                disconnected_clients.append(client_id)
        
        # 清理断开连接的客户端
        for client_id in disconnected_clients:
            if client_id in self.connected_clients:
                del self.connected_clients[client_id]
    
    async def send_to_client(self, client_id: str, message: dict):
        """发送消息到指定客户端"""
        if client_id not in self.connected_clients:
            logger.error(f"客户端 {client_id} 未连接")
            return False
        
        try:
            websocket = self.connected_clients[client_id]
            await websocket.send(json.dumps(message))
            return True
        except Exception as e:
            logger.error(f"发送消息到客户端 {client_id} 失败: {e}")
            return False
    
    def get_connected_clients(self) -> list:
        """获取已连接的客户端列表"""
        return list(self.connected_clients.keys())
    
    def get_client_count(self) -> int:
        """获取已连接的客户端数量"""
        return len(self.connected_clients)