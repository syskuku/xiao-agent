# xiao-agent - 小爱音箱智能控制中心

> 🎤 小爱音箱 + MCP协议 = 控制一切

## 🎯 核心理念

**小爱音箱作为MCP Client入口**，通过MCP协议调用各种工具，实现对浏览器、Windows系统、智能家居等的语音控制。

```
小爱音箱语音 → AI解析 → MCP协议 → 各种MCP Server → 执行操作
```

## 🚀 支持的控制方式

### 方式1：🌐 浏览器控制（Chrome插件）
直接控制Chrome浏览器执行操作。

**功能：**
- 打开网页、搜索内容
- 点击元素、输入文本
- 滚动页面、截图

**语音指令示例：**
- "小爱同学，打开百度"
- "小爱同学，搜索今天天气"
- "小爱同学，向下滚动"

### 方式2：🖥️ MCP控制（可扩展）
通过MCP协议控制Windows系统、文件系统等任何支持MCP的工具。

**功能：**
- 打开应用（记事本、计算器、文件管理器等）
- 执行系统命令
- 控制音量、截图、关机重启
- 锁定电脑

**语音指令示例：**
- "小爱同学，打开记事本"
- "小爱同学，打开计算器"
- "小爱同学，截图保存到桌面"
- "小爱同学，锁定电脑"
- "小爱同学，关机"

## 📦 快速部署

### Windows部署
```cmd
:: 1. 下载项目
cd C:\xiao-agent

:: 2. 运行部署脚本
scripts\setup.bat

:: 3. 编辑配置
notepad backend\config.json

:: 4. 启动服务
start.bat
```

### 配置示例 (backend/config.json)
```json
{
  "xiaomi": {
    "username": "您的小米账号",
    "password": "您的小米密码"
  },
  "openai_api": {
    "base_url": "https://api.openai.com/v1",
    "api_key": "您的API密钥",
    "model": "gpt-3.5-turbo"
  },
  "websocket": {
    "host": "localhost",
    "port": 8765
  },
  "mcp_servers": [
    {
      "name": "windows",
      "type": "stdio",
      "command": "python",
      "args": ["mcp_windows_server.py"]
    }
  ]
}
```

## 🔌 两种控制方式对比

| 控制方式 | 触发方式 | 适用场景 | 优点 |
|---------|---------|---------|------|
| **浏览器控制** | WebSocket + Chrome插件 | 网页操作 | 响应快、可视化 |
| **MCP控制** | MCP协议 | 系统操作、多工具 | 可扩展、支持多种工具 |

## 📁 项目结构

```
xiao-agent/
├── main.py                 # 主程序入口
├── mcp_client.py           # MCP客户端管理器
├── mcp_windows_server.py   # Windows系统MCP Server
├── mcp_browser_server.py   # 浏览器MCP Server（可选）
├── backend/
│   ├── conversation.py     # 对话记录获取
│   ├── ai_parser.py        # AI指令解析
│   └── websocket_server.py # WebSocket服务
├── browser_extension/      # Chrome浏览器插件
│   ├── manifest.json       # 插件配置
│   ├── background.js       # 后台脚本
│   ├── content.js          # 内容脚本
│   ├── popup.html          # 弹出窗口
│   ├── popup.js            # 弹出窗口逻辑
│   └── icons/              # 图标文件
├── scripts/                # 部署脚本
├── CONFIG_GUIDE.md         # 配置说明
├── MCP_INTEGRATION.md      # MCP集成文档
└── WINDOWS_DEPLOYMENT.md   # Windows部署指南
```

## 🔌 架构说明

```
┌─────────────────────────────────────────────────────────────┐
│                      小爱音箱                                │
│                   (语音指令入口)                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    xiao-agent 主程序                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ 对话记录    │  │ AI解析      │  │ MCP Client  │         │
│  │ 获取器      │  │ (OpenAI)    │  │ 管理器      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┴─────────────────┐
            ▼                                   ▼
┌───────────────────────┐         ┌───────────────────────┐
│  浏览器控制方式       │         │  MCP控制方式          │
│  WebSocket协议        │         │  MCP协议              │
└───────────────────────┘         └───────────────────────┘
            │                                   │
            ▼                                   ▼
┌───────────────────────┐         ┌───────────────────────┐
│  Chrome Extension     │         │  MCP Server 集群      │
│  - 打开网页           │         │  - Windows控制        │
│  - 点击元素           │         │  - 文件系统操作       │
│  - 输入文本           │         │  - 智能家居控制       │
│  - 截图               │         │  - 更多...            │
└───────────────────────┘         └───────────────────────┘
```

## 📖 详细文档

- **快速开始**: `WINDOWS_QUICKSTART.md`
- **配置说明**: `CONFIG_GUIDE.md`
- **MCP集成**: `MCP_INTEGRATION.md`
- **完整部署**: `WINDOWS_DEPLOYMENT.md`

## 📄 许可证

MIT License

## 🙏 致谢

- 基于 [xiaomusic](https://github.com/hanxi/xiaomusic)
- 使用 [MCP协议](https://modelcontextprotocol.io/)