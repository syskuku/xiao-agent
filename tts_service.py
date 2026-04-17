#!/usr/bin/env python3
"""
TTS服务 - 让小爱音箱说话
使用小米原生TTS服务，无需额外配置
"""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TTSService:
    """TTS服务类"""
    
    def __init__(self, xiaomi_config: dict):
        self.xiaomi_config = xiaomi_config
        self.mina_service = None
        self.device_id = None
        self._initialized = False
    
    async def initialize(self):
        """初始化TTS服务"""
        try:
            # 导入xiaomusic的依赖
            import sys
            sys.path.insert(0, '/opt/AstrBot/data/workspaces/webchat_FriendMessage_webchat_Syskuku_a9a18712-d45a-4e6d-a5cd-81e52e152187/xiaomusic')
            
            from miservice import MiAccount, MiNAService
            
            # 创建小米账号实例
            mi_account = MiAccount(
                self.xiaomi_config.get('username', ''),
                self.xiaomi_config.get('password', '')
            )
            
            # 创建MiNA服务实例
            self.mina_service = MiNAService(mi_account)
            
            # 获取设备ID
            await self._get_device_id()
            
            self._initialized = True
            logger.info("TTS服务初始化成功")
            
        except Exception as e:
            logger.error(f"TTS服务初始化失败: {e}")
            self._initialized = False
    
    async def _get_device_id(self):
        """获取小爱音箱设备ID"""
        try:
            # 获取设备列表
            devices = await self.mina_service.device_list()
            if devices:
                # 取第一个设备
                self.device_id = devices[0].get('deviceID')
                logger.info(f"获取到设备ID: {self.device_id}")
        except Exception as e:
            logger.error(f"获取设备ID失败: {e}")
    
    async def speak(self, text: str, device_id: str = None) -> bool:
        """
        让小爱音箱说话
        
        Args:
            text: 要播报的文本
            device_id: 设备ID（可选，使用默认设备）
        
        Returns:
            bool: 是否成功
        """
        if not self._initialized:
            logger.warning("TTS服务未初始化，无法播报")
            return False
        
        if not text:
            return False
        
        target_device = device_id or self.device_id
        if not target_device:
            logger.error("未找到设备ID")
            return False
        
        try:
            # 清理文本（移除可能导致问题的字符）
            clean_text = text.replace(" ", ",").replace("\n", "，")
            
            # 调用小米TTS服务
            await self.mina_service.text_to_speech(target_device, clean_text)
            logger.info(f"🔊 TTS播报成功: {clean_text}")
            return True
            
        except Exception as e:
            logger.error(f"TTS播报失败: {e}")
            return False
    
    async def speak_with_confirm(self, text: str, confirm_message: str = "好的") -> bool:
        """先播报确认消息，再播报主要内容"""
        await self.speak(confirm_message)
        await asyncio.sleep(0.5)
        return await self.speak(text)
    
    async def announce_success(self, action: str, details: str = "") -> bool:
        """播报成功信息"""
        message = f"已完成{action}"
        if details:
            message += f"，{details}"
        return await self.speak(message)
    
    async def announce_error(self, action: str, error: str = "") -> bool:
        """播报错误信息"""
        message = f"{action}失败"
        if error:
            message += f"，{error}"
        return await self.speak(message)


# 全局TTS服务实例
tts_service: Optional[TTSService] = None


def get_tts_service(xiaomi_config: dict = None) -> TTSService:
    """获取TTS服务实例"""
    global tts_service
    if tts_service is None and xiaomi_config:
        tts_service = TTSService(xiaomi_config)
    return tts_service


async def init_tts(xiaomi_config: dict) -> TTSService:
    """初始化TTS服务"""
    global tts_service
    tts_service = TTSService(xiaomi_config)
    await tts_service.initialize()
    return tts_service


async def speak(text: str, device_id: str = None) -> bool:
    """快捷函数：让小爱说话"""
    if tts_service:
        return await tts_service.speak(text, device_id)
    return False