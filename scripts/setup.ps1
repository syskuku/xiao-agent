# 小爱音箱 + 小米Mimo模型 + 浏览器控制系统 - Windows PowerShell部署脚本

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "小爱音箱浏览器控制系统 - Windows部署脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python
Write-Host "[INFO] 检查Python环境..." -ForegroundColor Blue
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[SUCCESS] 找到Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] 未找到Python，请先安装Python 3.8+" -ForegroundColor Red
    Write-Host "请访问 https://www.python.org/downloads/ 下载安装" -ForegroundColor Yellow
    Read-Host "按Enter键退出"
    exit 1
}

# 检查Chrome
Write-Host "[INFO] 检查Chrome浏览器..." -ForegroundColor Blue
$chromePath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
if (Test-Path $chromePath) {
    Write-Host "[SUCCESS] 找到Chrome浏览器" -ForegroundColor Green
} else {
    Write-Host "[WARNING] 未找到Chrome浏览器" -ForegroundColor Yellow
    Write-Host "请确保已安装Chrome浏览器以使用浏览器插件" -ForegroundColor Yellow
}

# 创建虚拟环境
Write-Host "[INFO] 创建Python虚拟环境..." -ForegroundColor Blue
if (-not (Test-Path "backend\venv")) {
    python -m venv backend\venv
    Write-Host "[SUCCESS] 虚拟环境创建完成" -ForegroundColor Green
} else {
    Write-Host "[INFO] 虚拟环境已存在" -ForegroundColor Blue
}

# 激活虚拟环境并安装依赖
Write-Host "[INFO] 安装Python依赖..." -ForegroundColor Blue
& "backend\venv\Scripts\Activate.ps1"

# 升级pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r backend\requirements.txt

Write-Host "[SUCCESS] Python依赖安装完成" -ForegroundColor Green

# 生成图标
Write-Host "[INFO] 生成浏览器插件图标..." -ForegroundColor Blue
Set-Location browser_extension\icons

# 尝试安装图标生成依赖
pip install cairosvg Pillow 2>$null

# 运行图标转换脚本
if (Test-Path "convert_icons.py") {
    python convert_icons.py
} else {
    Write-Host "[WARNING] 图标转换脚本不存在" -ForegroundColor Yellow
}

Set-Location ..\..

# 配置系统
Write-Host "[INFO] 配置系统..." -ForegroundColor Blue
if (-not (Test-Path "backend\config.json")) {
    Write-Host "[INFO] 创建配置文件..." -ForegroundColor Blue
    Copy-Item backend\config.example.json backend\config.json
    Write-Host "[WARNING] 请编辑 backend\config.json 文件，填入您的配置信息：" -ForegroundColor Yellow
    Write-Host "[WARNING]   - 小米账号和密码" -ForegroundColor Yellow
    Write-Host "[WARNING]   - 小米Mimo API Key" -ForegroundColor Yellow
    Write-Host "[WARNING]   - WebSocket端口等" -ForegroundColor Yellow
} else {
    Write-Host "[SUCCESS] 配置文件已存在" -ForegroundColor Green
}

# 创建启动脚本
Write-Host "[INFO] 创建启动脚本..." -ForegroundColor Blue
@"
@echo off
echo 正在启动小爱音箱浏览器控制系统...
echo.

cd backend
call venv\Scripts\activate.bat

if not exist "config.json" (
    echo 错误: 未找到配置文件 config.json
    echo 请复制 config.example.json 为 config.json 并填写配置
    pause
    exit /b 1
)

echo 启动后端服务...
python main.py

pause
"@ | Out-File -FilePath "start.bat" -Encoding ASCII

Write-Host "[SUCCESS] 启动脚本已创建: start.bat" -ForegroundColor Green

# 创建PowerShell启动脚本
Write-Host "[INFO] 创建PowerShell启动脚本..." -ForegroundColor Blue
@"
Write-Host "正在启动小爱音箱浏览器控制系统..." -ForegroundColor Cyan
Write-Host ""

Set-Location backend
& "venv\Scripts\Activate.ps1"

if (-not (Test-Path "config.json")) {
    Write-Host "错误: 未找到配置文件 config.json" -ForegroundColor Red
    Write-Host "请复制 config.example.json 为 config.json 并填写配置" -ForegroundColor Yellow
    Read-Host "按Enter键退出"
    exit 1
}

Write-Host "启动后端服务..." -ForegroundColor Green
python main.py

Read-Host "按Enter键退出"
"@ | Out-File -FilePath "start.ps1" -Encoding UTF8

Write-Host "[SUCCESS] PowerShell启动脚本已创建: start.ps1" -ForegroundColor Green

# 创建停止脚本
Write-Host "[INFO] 创建停止脚本..." -ForegroundColor Blue
@"
@echo off
echo 正在停止小爱音箱浏览器控制系统...
echo.

taskkill /F /IM python.exe /FI "WINDOWTITLE eq main.py"

echo 服务已停止
echo.

pause
"@ | Out-File -FilePath "stop.bat" -Encoding ASCII

Write-Host "[SUCCESS] 停止脚本已创建: stop.bat" -ForegroundColor Green

# 创建快速入门指南
Write-Host "[INFO] 创建Windows快速入门指南..." -ForegroundColor Blue
@"
# Windows快速入门指南

## 1. 配置系统

编辑 `backend\config.json` 文件：

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
  }
}
```

## 2. 启动后端服务

### 方法1：使用批处理文件
```cmd
start.bat
```

### 方法2：使用PowerShell
```powershell
.\start.ps1
```

## 3. 安装浏览器插件

1. 打开Chrome浏览器
2. 访问 `chrome://extensions/`
3. 开启"开发者模式"
4. 点击"加载已解压的扩展程序"
5. 选择 `browser_extension` 目录

## 4. 配置插件

1. 点击Chrome工具栏中的插件图标
2. 在"设置"标签页中配置WebSocket连接
3. 点击"连接"按钮

## 5. 测试系统

对小爱音箱说：
- "小爱同学，打开百度"
- "小爱同学，搜索最新新闻"
- "小爱同学，向下滚动"

## 获取小米Mimo API Key

1. 访问 https://platform.xiaomimimo.com/
2. 注册并登录
3. 在控制台中创建API Key
4. 将API Key填入配置文件

## 故障排除

### 问题1：Python虚拟环境激活失败
- 确保已安装Python
- 尝试使用管理员权限运行PowerShell

### 问题2：依赖安装失败
- 检查网络连接
- 尝试使用国内镜像源：
  ```cmd
  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```

### 问题3：Chrome插件加载失败
- 确保选择了正确的目录
- 检查是否有错误信息
- 尝试重新加载插件

## 常用命令

### 启动系统
```cmd
start.bat
```
或
```powershell
.\start.ps1
```

### 停止系统
```cmd
stop.bat
```

### 查看日志
- 后端日志：`backend\system.log`
- 插件日志：在Chrome插件弹出窗口中查看"日志"标签页
"@ | Out-File -FilePath "QUICKSTART_WINDOWS.md" -Encoding UTF8

Write-Host "[SUCCESS] Windows快速入门指南已创建: QUICKSTART_WINDOWS.md" -ForegroundColor Green

Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] Windows部署完成！" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作：" -ForegroundColor Yellow
Write-Host "1. 编辑 backend\config.json 文件" -ForegroundColor White
Write-Host "2. 运行 start.bat 或 .\start.ps1 启动服务" -ForegroundColor White
Write-Host "3. 安装Chrome浏览器插件" -ForegroundColor White
Write-Host "4. 参考 QUICKSTART_WINDOWS.md 文件" -ForegroundColor White
Write-Host ""
Read-Host "按Enter键退出"