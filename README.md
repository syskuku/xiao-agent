# 小爱音箱 + 小米Mimo模型 + 浏览器控制系统

## 系统概述

本系统基于 `xiaomusic` 项目原理，实现通过小爱音箱语音指令控制浏览器的完整解决方案。系统使用小米Mimo模型（OpenAI兼容格式）解析自然语言指令，并通过浏览器插件执行相应的浏览器操作。

## 系统架构

```
小爱音箱语音 → 小米云端 → xiaomusic对话记录获取 → 小米Mimo模型解析 → WebSocket转发 → Chrome插件 → 浏览器操作
```

## 核心组件

### 1. 后端服务 (Python)
- 基于 `xiaomusic` 修改，保留其对话记录获取功能
- 集成小米Mimo模型API（OpenAI兼容格式）
- WebSocket服务器，用于与浏览器插件通信
- 指令解析和路由

### 2. 浏览器插件 (Chrome Extension)
- Manifest V3 架构
- WebSocket客户端连接后端服务
- 浏览器自动化引擎（使用Chrome DevTools Protocol）
- 支持多种浏览器操作

### 3. 通信协议
- 基于JSON的指令格式
- 双向WebSocket通信
- 心跳机制和重连逻辑

## 快速开始

### 前置条件
1. 小米账号和密码
2. 小爱音箱设备
3. 小米Mimo模型API Key（从 platform.xiaomimimo.com 获取）
4. Chrome浏览器

### 部署步骤

#### 🐧 Linux/Mac 部署
```bash
# 1. 运行部署脚本
chmod +x scripts/setup.sh
./scripts/setup.sh

# 2. 配置系统
nano backend/config.json  # 编辑配置文件

# 3. 启动服务
./start.sh
```

#### 🪟 Windows 部署
```cmd
:: 1. 运行部署脚本（CMD）
cd scripts
setup.bat

:: 或者使用PowerShell
cd scripts
.\setup.ps1

:: 2. 配置系统
notepad backend\config.json  # 编辑配置文件

:: 3. 启动服务
start.bat
:: 或者
.\start.ps1
```

#### 详细部署指南
- **Linux/Mac**: 参考 `README.md` 本文件
- **Windows**: 参考 `WINDOWS_DEPLOYMENT.md` 文件
- **快速入门**: 参考 `QUICKSTART_WINDOWS.md` 文件（部署脚本自动生成）

#### 步骤1：配置后端服务
```bash
# Linux/Mac
cd backend
cp config.example.json config.json
nano config.json  # 编辑配置文件

# Windows
cd backend
copy config.example.json config.json
notepad config.json  # 编辑配置文件
```

#### 步骤2：启动后端服务
```bash
pip install -r requirements.txt
python main.py
```

#### 步骤3：安装浏览器插件
1. 打开Chrome浏览器，进入 `chrome://extensions/`
2. 开启"开发者模式"
3. 点击"加载已解压的扩展程序"
4. 选择 `browser_extension` 目录

#### 步骤4：测试系统
对小爱音箱说："小爱同学，打开百度"

## 支持的指令类型

### 基础操作
- `open_url` - 打开网页
- `click` - 点击元素
- `input` - 输入文本
- `scroll` - 滚动页面
- `screenshot` - 截图
- `navigate` - 页面导航
- `back/forward` - 前进后退

### 智能操作
- `extract` - 提取数据
- `search` - 搜索内容
- `fill_form` - 填写表单
- `multi_step` - 多步骤任务

## 项目结构

```
xiaomi_mimo_browser_control/
├── backend/                 # 后端Python服务
│   ├── main.py             # 主程序入口
│   ├── config.json         # 配置文件
│   ├── conversation.py     # 对话记录获取（基于xiaomusic）
│   ├── ai_parser.py        # AI指令解析（小米Mimo）
│   ├── websocket_server.py # WebSocket服务器
│   └── requirements.txt    # Python依赖
├── browser_extension/      # Chrome浏览器插件
│   ├── manifest.json       # 插件配置
│   ├── background.js       # 后台脚本
│   ├── content.js          # 内容脚本
│   ├── popup.html          # 弹出窗口
│   ├── popup.js            # 弹出窗口逻辑
│   └── icons/              # 图标文件
├── docs/                   # 文档
└── scripts/                # 部署脚本
```

## 技术栈

### 后端
- Python 3.9+
- aiohttp (异步HTTP)
- websockets (WebSocket)
- 小米Mimo模型API (OpenAI兼容)

### 浏览器插件
- Chrome Extension Manifest V3
- Chrome DevTools Protocol
- WebSocket API

## 配置说明

### config.json
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
  },
  "websocket": {
    "host": "localhost",
    "port": 8765
  },
  "browser_control": {
    "enable_ai": true,
    "default_timeout": 10
  }
}
```

## 安全注意事项

1. **API密钥安全**：不要将API密钥提交到版本控制系统
2. **网络安全**：建议在本地网络使用，如需公网访问请配置HTTPS
3. **权限控制**：浏览器插件需要谨慎授予权限
4. **操作确认**：敏感操作（如支付）需要用户确认

## 扩展开发

### 添加新的浏览器操作
1. 在 `ai_parser.py` 中添加新的操作类型
2. 在 `background.js` 中实现对应的执行函数
3. 更新指令解析提示词

### 自定义AI模型
修改 `config.json` 中的 `mimo_api` 配置，可以使用其他OpenAI兼容的模型。

## 故障排除

### 常见问题
1. **对话记录获取失败**：检查小米账号密码是否正确
2. **AI解析失败**：检查Mimo API Key是否有效
3. **插件连接失败**：确保后端WebSocket服务正在运行
4. **浏览器操作失败**：检查Chrome扩展权限设置

## 许可证

MIT License

## 致谢

- 基于 [xiaomusic](https://github.com/hanxi/xiaomusic) 项目
- 使用 [小米Mimo模型](https://platform.xiaomimimo.com/)
- 参考 [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)