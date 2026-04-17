# Windows MCP 集成指南

## 什么是MCP？

**MCP (Model Context Protocol)** 是微软推出的开放协议，用于标准化AI应用与外部工具和数据源之间的集成。通过MCP，AI助手（如Windows Copilot、Claude Desktop等）可以调用自定义工具来扩展功能。

## xiao-agent MCP Server

本项目提供了一个MCP Server，让AI助手能够控制浏览器执行各种操作。

### 可用工具

| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `browser_open_url` | 打开网页 | `url`: 网址 |
| `browser_search` | 搜索内容 | `query`: 关键词, `engine`: 搜索引擎(baidu/google/bing) |
| `browser_click` | 点击元素 | `selector`: CSS选择器 |
| `browser_input` | 输入文本 | `selector`: CSS选择器, `text`: 文本 |
| `browser_scroll` | 滚动页面 | `direction`: 方向(up/down), `amount`: 像素 |
| `browser_extract` | 提取数据 | `selector`: CSS选择器, `attribute`: 属性(text/html/value) |
| `browser_navigate` | 导航到新页面 | `url`: 网址 |
| `browser_back` | 返回上一页 | 无 |
| `browser_forward` | 前进到下一页 | 无 |
| `browser_get_page_info` | 获取页面信息 | 无 |

## 安装步骤

### 1. 安装MCP依赖

```bash
pip install mcp
```

### 2. 确保后端服务运行

MCP Server需要连接到xiao-agent的WebSocket服务，请确保后端服务已启动：

```bash
cd backend
python main.py
```

### 3. 配置MCP

#### Windows Copilot 配置

在Windows上，创建或编辑MCP配置文件：

**文件位置**: `%APPDATA%\mcp\config.json` 或 `C:\Users\{用户名}\.mcp\config.json`

```json
{
  "mcpServers": {
    "xiao-agent-browser": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "C:\\path\\to\\xiao-agent",
      "env": {
        "PYTHONPATH": "C:\\path\\to\\xiao-agent"
      }
    }
  }
}
```

#### Claude Desktop 配置

**文件位置**: `~/.config/claude/claude_desktop_config.json` (Linux/Mac) 或 `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

```json
{
  "mcpServers": {
    "xiao-agent-browser": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "C:\\path\\to\\xiao-agent"
    }
  }
}
```

#### Cursor 配置

在Cursor中，编辑 `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "xiao-agent-browser": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/xiao-agent"
    }
  }
}
```

## 使用示例

配置完成后，你可以在AI助手中使用自然语言调用浏览器功能：

### 示例1：打开网页
```
用户: 帮我打开百度
AI: 我来帮你打开百度。
[调用 browser_open_url 工具，url="https://www.baidu.com"]
```

### 示例2：搜索内容
```
用户: 搜索今天的天气
AI: 我来帮你搜索今天的天气。
[调用 browser_search 工具，query="今天天气", engine="baidu"]
```

### 示例3：多步骤操作
```
用户: 帮我在淘宝搜索iPhone 15
AI: 我来帮你完成这个操作。
1. [调用 browser_open_url 打开淘宝]
2. [调用 browser_input 在搜索框输入"iPhone 15"]
3. [调用 browser_click 点击搜索按钮]
```

## 故障排除

### 问题1：MCP Server无法启动
- 检查Python路径是否正确
- 确认mcp包已安装：`pip install mcp`
- 检查cwd路径是否正确

### 问题2：无法连接到浏览器
- 确保xiao-agent后端服务正在运行
- 检查WebSocket端口（默认8765）是否被占用
- 确认Chrome插件已安装并连接

### 问题3：工具调用失败
- 检查后端服务日志
- 确认Chrome浏览器已打开
- 尝试重启后端服务

## 技术架构

```
┌─────────────────────────────────────────────────────────┐
│              AI Assistant (Copilot/Claude)              │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   MCP Protocol                          │
│                  (stdio transport)                      │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              mcp_server.py (FastMCP)                    │
│         ┌─────────────────────────────────┐            │
│         │  mcp_tools.py (BrowserTools)    │            │
│         └─────────────────────────────────┘            │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│            WebSocket (localhost:8765)                   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Chrome Extension (background.js)           │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    浏览器操作                            │
└─────────────────────────────────────────────────────────┘
```

## 高级配置

### 自定义端口

如果WebSocket端口不是默认的8765，可以在启动时指定：

```json
{
  "mcpServers": {
    "xiao-agent-browser": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "C:\\path\\to\\xiao-agent",
      "env": {
        "WS_PORT": "9999"
      }
    }
  }
}
```

### 环境变量

支持以下环境变量：

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `WS_HOST` | WebSocket主机 | localhost |
| `WS_PORT` | WebSocket端口 | 8765 |
| `LOG_LEVEL` | 日志级别 | INFO |

## 相关资源

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Windows MCP 文档](https://learn.microsoft.com/zh-cn/windows/ai/mcp/overview)