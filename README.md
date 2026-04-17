# xiao-agent - 小爱音箱智能控制中心

> 🎤 小爱音箱 + MCP协议 = 控制一切

## 🎯 核心理念

**小爱音箱作为MCP Client入口**，通过MCP协议调用各种工具，实现对浏览器、Windows系统、智能家居等的语音控制。

```
小爱音箱语音 → AI解析 → MCP协议 → 各种MCP Server → 执行操作
```

## 🚀 支持的控制能力

### 🌐 浏览器控制
- 打开网页、搜索内容、点击元素、输入文本
- 支持百度、谷歌、必应等搜索引擎

### 🖥️ Windows系统控制
- 打开应用（记事本、计算器、文件管理器等）
- 执行系统命令
- 控制音量、截图、关机重启
- 锁定电脑

### 📁 文件系统操作
- 读写文件、创建目录
- 搜索文件、复制移动

### 🔌 可扩展
- 任何支持MCP协议的工具都可以接入
- 自定义MCP Server开发简单

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
  "mcp_servers": [
    {
      "name": "windows",
      "type": "stdio",
      "command": "python",
      "args": ["mcp_windows_server.py"]
    },
    {
      "name": "browser",
      "type": "stdio",
      "command": "python",
      "args": ["mcp_browser_server.py"]
    }
  ]
}
```

## 🎤 使用示例

### 语音指令示例
| 语音指令 | 执行操作 |
|---------|---------|
| "小爱同学，打开百度" | 浏览器打开百度 |
| "小爱同学，搜索今天天气" | 百度搜索天气 |
| "小爱同学，打开记事本" | 启动Windows记事本 |
| "小爱同学，打开计算器" | 启动Windows计算器 |
| "小爱同学，截图" | 截取屏幕截图 |
| "小爱同学，锁定电脑" | 锁定Windows |
| "小爱同学，关机" | 关闭电脑 |

## 📁 项目结构

```
xiao-agent/
├── main.py                 # 主程序入口
├── mcp_client.py           # MCP客户端管理器
├── mcp_windows_server.py   # Windows系统MCP Server
├── mcp_browser_server.py   # 浏览器MCP Server
├── backend/
│   ├── conversation.py     # 对话记录获取
│   ├── ai_parser.py        # AI指令解析
│   └── websocket_server.py # WebSocket服务
├── browser_extension/      # Chrome插件
├── scripts/                # 部署脚本
└── 文档/
    ├── CONFIG_GUIDE.md     # 配置说明
    ├── MCP_INTEGRATION.md  # MCP集成文档
    └── WINDOWS_DEPLOYMENT.md
```

## 🔌 MCP架构

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
                              ▼ MCP协议
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server 集群                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ 浏览器      │  │ Windows     │  │ 文件系统    │         │
│  │ MCP Server  │  │ MCP Server  │  │ MCP Server  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    执行结果                                  │
│        浏览器操作 / 系统命令 / 文件操作 / 更多...            │
└─────────────────────────────────────────────────────────────┘
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