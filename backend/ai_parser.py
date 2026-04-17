#!/usr/bin/env python3
"""
AI指令解析器 - 使用小米Mimo模型
将自然语言指令转换为结构化的浏览器操作
"""

import json
import logging
import aiohttp
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# 浏览器控制指令提示词
BROWSER_CONTROL_PROMPT = """
你是一个专业的浏览器控制指令解析器，负责将用户的自然语言指令转换为结构化的JSON操作指令。

## 支持的操作类型

### 1. 页面导航
- **open_url**: 打开网页
  ```json
  {"action": "open_url", "params": {"url": "https://example.com"}}
  ```

- **navigate**: 在当前标签页导航到新网址
  ```json
  {"action": "navigate", "params": {"url": "https://example.com"}}
  ```

- **back**: 返回上一页
  ```json
  {"action": "back", "params": {}}
  ```

- **forward**: 前进到下一页
  ```json
  {"action": "forward", "params": {}}
  ```

### 2. 元素交互
- **click**: 点击元素
  ```json
  {"action": "click", "params": {"selector": "#button-id", "description": "搜索按钮"}}
  ```

- **input**: 输入文本
  ```json
  {"action": "input", "params": {"selector": "input[name='q']", "text": "搜索内容"}}
  ```

- **scroll**: 滚动页面
  ```json
  {"action": "scroll", "params": {"direction": "down", "amount": 500}}
  ```

### 3. 数据操作
- **screenshot**: 截取当前页面截图
  ```json
  {"action": "screenshot", "params": {"full_page": false}}
  ```

- **extract**: 提取页面数据
  ```json
  {"action": "extract", "params": {"selector": ".product-price", "attribute": "text"}}
  ```

- **get_text**: 获取元素文本
  ```json
  {"action": "get_text", "params": {"selector": "h1.title"}}
  ```

### 4. 搜索操作
- **search**: 搜索内容
  ```json
  {"action": "search", "params": {"keyword": "搜索关键词", "engine": "baidu"}}
  ```

### 5. 表单操作
- **fill_form**: 填写表单
  ```json
  {"action": "fill_form", "params": {"fields": [{"selector": "#username", "value": "test"}]}}
  ```

### 6. 高级操作
- **wait**: 等待一段时间
  ```json
  {"action": "wait", "params": {"seconds": 2}}
  ```

- **multi_step**: 多步骤操作
  ```json
  {"action": "multi_step", "params": {"steps": [...]}}
  ```

## 解析规则

1. **准确性**: 必须准确理解用户意图
2. **完整性**: 提供所有必要的参数
3. **智能性**: 如果指令不明确，可以推断合理参数
4. **安全性**: 避免危险操作（如删除数据、支付等）

## 响应格式

请严格按照以下JSON格式响应：

```json
{
  "action": "操作类型",
  "params": {
    "参数1": "值1",
    "参数2": "值2"
  },
  "reasoning": "简要说明你的解析思路",
  "confidence": 0.95
}
```

如果无法解析指令，请返回：
```json
{
  "action": "clarify",
  "message": "需要更多信息来理解您的指令",
  "suggestions": ["建议1", "建议2"]
}
```

## 示例

用户指令: "打开百度并搜索iPhone 15价格"
响应:
```json
{
  "action": "multi_step",
  "params": {
    "steps": [
      {"action": "open_url", "params": {"url": "https://www.baidu.com"}},
      {"action": "input", "params": {"selector": "#kw", "text": "iPhone 15价格"}},
      {"action": "click", "params": {"selector": "#su"}}
    ]
  },
  "reasoning": "用户想要打开百度并搜索特定内容，需要执行多个步骤",
  "confidence": 0.98
}
```
"""

class AIParser:
    """AI指令解析器"""
    
    def __init__(self, mimo_config: dict):
        """初始化AI解析器"""
        self.config = mimo_config
        self.base_url = mimo_config.get('base_url', 'https://api.xiaomimimo.com/v1')
        self.api_key = mimo_config.get('api_key', '')
        self.model = mimo_config.get('model', 'MiMo-V2-Flash')
        
        if not self.api_key:
            logger.warning("未配置Mimo API Key，AI解析功能将不可用")
    
    async def parse_command(self, command: str) -> Optional[Dict[str, Any]]:
        """解析用户指令"""
        if not self.api_key:
            logger.error("Mimo API Key未配置")
            return None
        
        try:
            # 构建请求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = [
                {"role": "system", "content": BROWSER_CONTROL_PROMPT},
                {"role": "user", "content": f"用户指令：{command}"}
            ]
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.1,  # 低温度以获得更一致的结果
                "max_tokens": 500,
                "response_format": {"type": "json_object"}  # 强制JSON响应
            }
            
            # 发送请求
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]
                        
                        # 解析JSON响应
                        try:
                            parsed = json.loads(content)
                            logger.debug(f"AI解析结果: {parsed}")
                            return parsed
                        except json.JSONDecodeError as e:
                            logger.error(f"AI响应JSON解析失败: {e}")
                            logger.debug(f"原始响应: {content}")
                            return None
                    else:
                        logger.error(f"AI API请求失败，状态码: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"AI解析指令失败: {e}")
            return None
    
    async def test_connection(self) -> bool:
        """测试AI连接"""
        try:
            result = await self.parse_command("测试连接")
            return result is not None
        except Exception:
            return False