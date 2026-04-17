# Windows 快速启动指南

## 📋 完整部署流程

### 步骤1：下载项目
```cmd
:: 打开CMD，进入项目目录
cd C:\path\to\xiao-agent
```

### 步骤2：运行部署脚本
```cmd
:: 运行Windows部署脚本
scripts\setup.bat
```

### 步骤3：配置系统
```cmd
:: 编辑配置文件
notepad backend\config.json
```

配置示例：
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
  }
}
```

### 步骤4：启动后端服务
```cmd
start.bat
```

### 步骤5：安装Chrome插件
1. 打开Chrome浏览器
2. 访问 `chrome://extensions/`
3. 开启"开发者模式"
4. 点击"加载已解压的扩展程序"
5. 选择 `browser_extension` 目录
6. 点击插件图标，配置WebSocket连接（localhost:8765）

### 步骤6：测试语音控制
对小爱音箱说：
- "小爱同学，打开百度"
- "小爱同学，搜索今天天气"

---

## 🔌 可选：Windows MCP集成

如果想让Copilot等AI助手也能控制浏览器：

### 步骤1：安装MCP依赖
```cmd
cd backend
venv\Scripts\activate.bat
pip install mcp
```

### 步骤2：配置MCP

创建文件 `%APPDATA%\mcp\config.json`：
```json
{
  "mcpServers": {
    "xiao-agent-browser": {
      "command": "C:\\path\\to\\xiao-agent\\backend\\venv\\Scripts\\python.exe",
      "args": ["mcp_server.py"],
      "cwd": "C:\\path\\to\\xiao-agent"
    }
  }
}
```

### 步骤3：在Copilot中使用
打开Windows Copilot，说：
- "帮我打开淘宝搜索iPhone"
- "在百度搜索今天的新闻"

---

## 🎯 完整控制链路

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  小爱音箱   │    │  后端服务   │    │ Chrome插件  │    │   浏览器    │
│  语音指令   │───▶│  AI解析     │───▶│  执行操作   │───▶│  打开网页   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Copilot   │    │  MCP Server │    │ Chrome插件  │    │   浏览器    │
│  AI指令     │───▶│  工具调用   │───▶│  执行操作   │───▶│  打开网页   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## 📞 故障排除

### 问题1：后端服务启动失败
- 检查Python是否安装
- 检查config.json配置是否正确
- 查看日志文件

### 问题2：Chrome插件连接失败
- 确保后端服务正在运行
- 检查WebSocket端口（8765）是否被占用
- 重新加载Chrome插件

### 问题3：语音指令无响应
- 检查小米账号配置
- 确保小爱音箱已登录同一账号
- 查看后端日志

## 📚 详细文档

- **完整部署**: `WINDOWS_DEPLOYMENT.md`
- **配置说明**: `CONFIG_GUIDE.md`
- **MCP集成**: `MCP_INTEGRATION.md`
- **检查清单**: `WINDOWS_CHECKLIST.md`