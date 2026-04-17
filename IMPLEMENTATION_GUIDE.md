# 小爱音箱 + 小米Mimo模型 + 浏览器控制系统 - 实现指南

## 系统概述

本系统基于 `xiaomusic` 项目原理，实现了通过小爱音箱语音指令控制浏览器的完整解决方案。系统使用小米Mimo模型（OpenAI兼容格式）解析自然语言指令，并通过Chrome浏览器插件执行相应的浏览器操作。

## 核心思路

### 1. 语音指令获取（基于xiaomusic原理）
- **对话记录轮询**：定期向小米服务器请求小爱音箱的最新对话记录
- **API接口**：使用小米的 `userprofile.mina.mi.com` API获取对话数据
- **数据解析**：从API响应中提取用户的语音指令文本

### 2. AI指令解析（小米Mimo模型）
- **OpenAI兼容格式**：使用小米Mimo模型的OpenAI兼容API
- **智能解析**：将自然语言指令转换为结构化的浏览器操作指令
- **提示词工程**：设计专门的提示词，让AI理解浏览器控制指令

### 3. 实时通信（WebSocket）
- **双向通信**：后端服务与浏览器插件通过WebSocket实时通信
- **指令转发**：将AI解析后的指令发送到浏览器插件
- **状态同步**：实时同步连接状态和执行结果

### 4. 浏览器自动化（Chrome扩展）
- **Manifest V3**：使用最新的Chrome扩展架构
- **多种操作**：支持点击、输入、滚动、截图等浏览器操作
- **智能执行**：根据AI解析的指令执行相应的浏览器操作

## 技术架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   小爱音箱      │    │   小米云端      │    │   后端服务      │
│                 │───▶│                 │───▶│                 │
│  语音指令       │    │  对话记录API    │    │  对话记录获取   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                               ┌─────────────────┐
                                               │   小米Mimo模型  │
                                               │                 │
                                               │  AI指令解析     │
                                               └─────────────────┘
                                                       │
                                                       ▼
                                               ┌─────────────────┐
                                               │   WebSocket     │
                                               │   服务器        │
                                               └─────────────────┘
                                                       │
                                                       ▼
                                               ┌─────────────────┐
                                               │  Chrome插件     │
                                               │                 │
                                               │  浏览器自动化   │
                                               └─────────────────┘
                                                       │
                                                       ▼
                                               ┌─────────────────┐
                                               │   目标网站      │
                                               │                 │
                                               │  执行操作       │
                                               └─────────────────┘
```

## 实现细节

### 1. 对话记录获取模块 (`conversation.py`)

**核心功能**：
- 轮询小米API获取对话记录
- 解析JSON响应，提取用户指令
- 检测新指令并触发处理流程

**关键代码**：
```python
async def pull_conversation(self, device_id: str, device_info: dict):
    """拉取单个设备的对话记录"""
    url = LATEST_ASK_API.format(
        hardware=hardware,
        timestamp=str(int(time.time() * 1000))
    )
    
    async with self.session.get(url, timeout=timeout, cookies=cookies) as response:
        if response.status == 200:
            data = await response.json()
            await self.process_conversation_data(device_id, data)
```

### 2. AI指令解析模块 (`ai_parser.py`)

**核心功能**：
- 使用小米Mimo模型API解析自然语言
- 将指令转换为结构化JSON格式
- 支持多种浏览器操作类型

**关键代码**：
```python
async def parse_command(self, command: str) -> Optional[Dict[str, Any]]:
    """解析用户指令"""
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
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
```

### 3. WebSocket通信模块 (`websocket_server.py`)

**核心功能**：
- 管理浏览器插件连接
- 广播指令到所有连接的客户端
- 处理心跳和重连机制

**关键代码**：
```python
async def broadcast(self, message: dict):
    """广播消息到所有连接的客户端"""
    message_json = json.dumps(message)
    
    for client_id, websocket in self.connected_clients.items():
        try:
            await websocket.send(message_json)
        except websockets.exceptions.ConnectionClosed:
            disconnected_clients.append(client_id)
```

### 4. 浏览器插件模块 (`background.js`)

**核心功能**：
- WebSocket客户端连接
- 浏览器操作执行引擎
- 错误处理和重连机制

**关键代码**：
```javascript
async handleCommand(command) {
  switch (command.action) {
    case 'open_url':
      return await this.openUrl(command.params);
    case 'click':
      return await this.clickElement(command.params);
    case 'input':
      return await this.inputText(command.params);
    // ... 更多操作
  }
}
```

## 支持的指令类型

### 基础操作
1. **open_url** - 打开网页
2. **navigate** - 页面导航
3. **click** - 点击元素
4. **input** - 输入文本
5. **scroll** - 滚动页面
6. **screenshot** - 截图
7. **back/forward** - 前进后退

### 智能操作
8. **search** - 搜索内容
9. **extract** - 提取数据
10. **fill_form** - 填写表单
11. **multi_step** - 多步骤任务

## 部署和使用

### 步骤1：环境准备
```bash
# 克隆项目
git clone <项目地址>
cd xiaomi_mimo_browser_control

# 运行部署脚本
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 步骤2：配置系统
编辑 `backend/config.json`：
```json
{
  "xiaomi": {
    "username": "your_xiaomi_username",
    "password": "your_xiaomi_password"
  },
  "mimo_api": {
    "base_url": "https://api.xiaomimimo.com/v1",
    "api_key": "your_mimo_api_key",
    "model": "MiMo-V2-Flash"
  }
}
```

### 步骤3：启动服务
```bash
./start.sh
```

### 步骤4：安装浏览器插件
1. 打开Chrome浏览器
2. 访问 `chrome://extensions/`
3. 开启"开发者模式"
4. 点击"加载已解压的扩展程序"
5. 选择 `browser_extension` 目录

### 步骤5：测试系统
对小爱音箱说：
- "小爱同学，打开百度"
- "小爱同学，搜索iPhone 15"
- "小爱同学，向下滚动"

## 扩展和定制

### 1. 添加新的浏览器操作
1. 在 `ai_parser.py` 中更新提示词
2. 在 `background.js` 中实现新的操作函数
3. 在 `content.js` 中添加页面内操作支持

### 2. 自定义AI模型
修改 `config.json` 中的 `mimo_api` 配置，可以使用其他OpenAI兼容的模型。

### 3. 增加错误处理
- 实现重试机制
- 添加用户确认步骤
- 增加操作日志记录

## 安全考虑

### 1. API密钥安全
- 不要将API密钥提交到版本控制系统
- 使用环境变量或加密存储

### 2. 网络安全
- 建议在本地网络使用
- 如需公网访问，请配置HTTPS

### 3. 权限控制
- 浏览器插件需要谨慎授予权限
- 敏感操作需要用户确认

## 故障排除

### 常见问题

1. **对话记录获取失败**
   - 检查小米账号密码
   - 确保小爱音箱已登录

2. **AI解析失败**
   - 检查Mimo API Key
   - 确保网络连接正常

3. **插件连接失败**
   - 确保后端服务运行
   - 检查WebSocket端口

4. **浏览器操作失败**
   - 检查Chrome扩展权限
   - 确保页面加载完成

## 性能优化

### 1. 减少API调用
- 实现指令缓存
- 批量处理相似指令

### 2. 提高响应速度
- 使用异步处理
- 优化WebSocket通信

### 3. 资源管理
- 限制并发连接数
- 清理无用资源

## 未来扩展

### 1. 多设备支持
- 支持多个小爱音箱
- 设备分组管理

### 2. 高级功能
- 视觉理解（截图分析）
- 学习优化（用户习惯）
- 语音反馈（TTS）

### 3. 集成其他平台
- 支持其他语音助手
- 集成更多AI模型

## 总结

本系统实现了从语音指令到浏览器控制的完整链路，具有以下特点：

1. **实时性**：WebSocket提供实时通信
2. **智能性**：小米Mimo模型理解自然语言
3. **可扩展性**：模块化设计，易于扩展
4. **易用性**：简单的配置和部署流程

通过这个系统，用户可以通过自然语言语音指令控制浏览器执行各种操作，大大提高了操作便利性和效率。