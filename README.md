# xiao-agent - 小爱音箱智能控制中心

通过小爱音箱语音控制浏览器和Windows系统。

## 快速开始

### Windows部署

```cmd
:: 1. 下载项目
git clone https://github.com/syskuku/xiao-agent.git
cd xiao-agent

:: 2. 运行部署脚本
scripts\setup.bat

:: 3. 编辑配置
notepad backend\config.json

:: 4. 启动服务
start.bat
```

### 配置说明

编辑 `backend\config.json`:

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
  }
}
```

### 语音指令示例

| 指令 | 功能 |
|------|------|
| "打开百度" | 浏览器打开百度 |
| "搜索天气" | 百度搜索天气 |
| "打开记事本" | 启动Windows记事本 |
| "打开计算器" | 启动Windows计算器 |

## 安装Chrome扩展

1. 打开Chrome，访问 `chrome://extensions/`
2. 开启"开发者模式"
3. 点击"加载已解压的扩展程序"
4. 选择 `browser_extension` 文件夹
5. 点击插件图标，配置连接（localhost:8765）

## 项目结构

```
xiao-agent/
├── backend/
│   ├── main.py          # 主程序
│   ├── conversation.py  # 对话记录获取
│   ├── ai_parser.py     # AI指令解析
│   └── websocket_server.py
├── browser_extension/   # Chrome插件
├── scripts/
│   └── setup.bat        # 部署脚本
└── start.bat            # 启动脚本
```

## 许可证

MIT License