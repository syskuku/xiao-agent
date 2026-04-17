# Windows部署指南

## 📋 系统要求

### 必需的软件
1. **Python 3.8+** - [下载地址](https://www.python.org/downloads/)
2. **Chrome浏览器** - [下载地址](https://www.google.com/chrome/)
3. **Git**（可选）- [下载地址](https://git-scm.com/)

### 必需的信息
1. **小米账号**和密码
2. **小米Mimo API Key** - 从 [platform.xiaomimimo.com](https://platform.xiaomimimo.com/) 获取

## 🚀 快速部署（推荐）

### 方法1：使用批处理文件（最简单）

#### 步骤1：下载项目
如果您有Git：
```cmd
git clone <项目地址>
cd xiaomi_mimo_browser_control
```

如果没有Git，手动下载并解压项目文件。

#### 步骤2：运行部署脚本
```cmd
cd scripts
setup.bat
```

#### 步骤3：配置系统
编辑 `backend\config.json` 文件，填入您的配置。

#### 步骤4：启动服务
```cmd
start.bat
```

### 方法2：使用PowerShell（更强大）

#### 步骤1：打开PowerShell
1. 按 `Win + X`，选择"Windows PowerShell"
2. 或者搜索"PowerShell"并打开

#### 步骤2：运行部署脚本
```powershell
cd scripts
.\setup.ps1
```

#### 步骤3：配置系统
编辑 `backend\config.json` 文件。

#### 步骤4：启动服务
```powershell
.\start.ps1
```

## 📝 详细部署步骤

### 步骤1：安装Python

1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载Python 3.8或更高版本
3. **重要**：安装时勾选"Add Python to PATH"
4. 验证安装：
   ```cmd
   python --version
   pip --version
   ```

### 步骤2：下载项目

#### 方法A：使用Git
```cmd
git clone <项目地址>
cd xiaomi_mimo_browser_control
```

#### 方法B：手动下载
1. 下载项目ZIP文件
2. 解压到任意目录
3. 打开命令提示符，进入项目目录

### 步骤3：运行部署脚本

#### 使用命令提示符（CMD）
```cmd
cd scripts
setup.bat
```

#### 使用PowerShell
```powershell
cd scripts
.\setup.ps1
```

**部署脚本会自动完成：**
- ✅ 检查Python环境
- ✅ 检查Chrome浏览器
- ✅ 创建Python虚拟环境
- ✅ 安装Python依赖
- ✅ 生成浏览器插件图标
- ✅ 创建配置文件模板
- ✅ 创建启动/停止脚本
- ✅ 生成Windows快速入门指南

### 步骤4：配置系统

#### 4.1 编辑配置文件
使用记事本或任何文本编辑器：
```cmd
notepad backend\config.json
```

#### 4.2 填写配置信息
```json
{
  "xiaomi": {
    "username": "您的小米账号",
    "password": "您的小米密码"
  },
  "mimo_api": {
    "base_url": "https://api.xiaomimimo.com/v1",
    "api_key": "您的Mimo API Key",
    "model": "MiMo-V2-Flash"
  },
  "websocket": {
    "host": "localhost",
    "port": 8765
  }
}
```

#### 4.3 获取小米Mimo API Key
1. 访问：https://platform.xiaomimimo.com/
2. 注册并登录
3. 进入控制台
4. 创建API Key
5. 复制API Key到配置文件

### 步骤5：启动后端服务

#### 方法1：使用批处理文件
```cmd
start.bat
```

#### 方法2：使用PowerShell
```powershell
.\start.ps1
```

#### 方法3：手动启动
```cmd
cd backend
venv\Scripts\activate.bat
python main.py
```

**启动成功后，您会看到：**
```
INFO - WebSocket服务器已启动: ws://localhost:8765
INFO - 系统启动完成，等待语音指令...
```

### 步骤6：安装Chrome浏览器插件

#### 6.1 打开Chrome扩展管理
1. 打开Chrome浏览器
2. 在地址栏输入：`chrome://extensions/`
3. 按回车

#### 6.2 启用开发者模式
1. 在右上角找到"开发者模式"开关
2. 点击开启

#### 6.3 加载插件
1. 点击"加载已解压的扩展程序"
2. 选择 `browser_extension` 目录
3. 点击"选择文件夹"

#### 6.4 验证插件安装
- 您应该在扩展列表中看到"小爱音箱浏览器控制器"
- Chrome工具栏会出现插件图标

### 步骤7：配置浏览器插件

#### 7.1 打开插件设置
1. 点击Chrome工具栏中的插件图标
2. 在弹出窗口中，您会看到连接状态

#### 7.2 配置WebSocket连接
1. 在"设置"标签页中
2. 主机地址：`localhost`
3. 端口：`8765`
4. 点击"连接"按钮

#### 7.3 验证连接
- 状态指示器应变为绿色
- 显示"已连接"

### 步骤8：测试系统

#### 8.1 测试基本功能
对小爱音箱说：
- "小爱同学，打开百度"
- "小爱同学，搜索最新新闻"
- "小爱同学，向下滚动"

#### 8.2 查看操作日志
1. 点击插件图标
2. 切换到"日志"标签页
3. 查看执行的操作记录

## 🔧 Windows特定问题解决

### 问题1：Python虚拟环境激活失败
```cmd
# 错误：无法加载文件 venv\Scripts\activate.ps1
# 解决：使用CMD而不是PowerShell
cd backend
venv\Scripts\activate.bat
```

### 问题2：依赖安装失败
```cmd
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题3：端口被占用
```cmd
# 查看端口占用
netstat -ano | findstr :8765

# 结束占用端口的进程
taskkill /PID <进程ID> /F
```

### 问题4：防火墙阻止
1. 打开"Windows Defender防火墙"
2. 点击"允许应用通过防火墙"
3. 添加Python到允许列表

### 问题5：Chrome插件加载失败
1. 确保选择了正确的目录（`browser_extension`）
2. 检查是否有错误信息
3. 尝试重新加载插件

## 📁 Windows项目结构

```
xiaomi_mimo_browser_control/
├── backend/                # 后端Python服务
│   ├── main.py           # 主程序
│   ├── conversation.py   # 对话记录获取
│   ├── ai_parser.py      # AI指令解析
│   ├── websocket_server.py # WebSocket服务器
│   ├── config.example.json # 配置文件模板
│   └── requirements.txt  # Python依赖
├── browser_extension/     # Chrome浏览器插件
│   ├── manifest.json     # 插件配置
│   ├── background.js     # 后台脚本
│   ├── content.js        # 内容脚本
│   ├── popup.html        # 弹出窗口
│   ├── popup.js          # 弹出窗口逻辑
│   └── icons/            # 图标文件
├── scripts/              # 部署脚本
│   ├── setup.bat         # Windows批处理部署脚本
│   ├── setup.ps1         # Windows PowerShell部署脚本
│   └── setup.sh          # Linux/Mac部署脚本
├── start.bat             # Windows启动脚本
├── start.ps1             # Windows PowerShell启动脚本
├── stop.bat              # Windows停止脚本
├── QUICKSTART_WINDOWS.md # Windows快速入门指南
└── WINDOWS_DEPLOYMENT.md # 本文件
```

## 🎯 Windows常用命令

### 启动系统
```cmd
# 方法1：批处理文件
start.bat

# 方法2：PowerShell
.\start.ps1

# 方法3：手动启动
cd backend
venv\Scripts\activate.bat
python main.py
```

### 停止系统
```cmd
# 方法1：批处理文件
stop.bat

# 方法2：任务管理器
# 打开任务管理器，结束python.exe进程

# 方法3：命令行
taskkill /F /IM python.exe
```

### 查看日志
```cmd
# 查看后端日志
type backend\system.log

# 或者使用PowerShell
Get-Content backend\system.log -Wait
```

### 重新部署
```cmd
# 清理并重新部署
rmdir /s /q backend\venv
del backend\config.json
scripts\setup.bat
```

## 🔒 Windows安全设置

### 1. 防火墙设置
- 确保端口8765没有被防火墙阻止
- 如果需要，添加Python到防火墙例外列表

### 2. 权限设置
- 确保对项目目录有读写权限
- 如果遇到权限问题，尝试以管理员身份运行

### 3. 杀毒软件
- 某些杀毒软件可能阻止Python脚本
- 将项目目录添加到杀毒软件的白名单

## 📞 获取帮助

如果遇到问题：
1. 查看 `QUICKSTART_WINDOWS.md` 文件
2. 查看 `IMPLEMENTATION_GUIDE.md` 文件
3. 检查系统日志文件
4. 参考故障排除部分

## 🎉 部署完成

恭喜！您已成功在Windows上部署小爱音箱浏览器控制系统。现在您可以：
- 通过语音指令控制浏览器
- 执行各种浏览器操作
- 享受智能化的交互体验

开始您的智能语音控制浏览器之旅吧！🎤🤖🌐