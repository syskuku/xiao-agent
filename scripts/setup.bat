@echo off
REM 小爱音箱 + 小米Mimo模型 + 浏览器控制系统 - Windows部署脚本

echo ==========================================
echo 小爱音箱浏览器控制系统 - Windows部署脚本
echo ==========================================

REM 检查Python
echo [INFO] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未找到Python，请先安装Python 3.8+
    echo 请访问 https://www.python.org/downloads/ 下载安装
    pause
    exit /b 1
)

echo [SUCCESS] 找到Python

REM 检查Chrome
echo [INFO] 检查Chrome浏览器...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] 找到Chrome浏览器
) else (
    echo [WARNING] 未找到Chrome浏览器
    echo 请确保已安装Chrome浏览器以使用浏览器插件
)

REM 创建虚拟环境
echo [INFO] 创建Python虚拟环境...
if not exist "backend\venv" (
    python -m venv backend\venv
    echo [SUCCESS] 虚拟环境创建完成
) else (
    echo [INFO] 虚拟环境已存在
)

REM 激活虚拟环境并安装依赖
echo [INFO] 安装Python依赖...
call backend\venv\Scripts\activate.bat

REM 升级pip
python -m pip install --upgrade pip

REM 安装依赖
pip install -r backend\requirements.txt

echo [SUCCESS] Python依赖安装完成

REM 生成图标
echo [INFO] 生成浏览器插件图标...
cd browser_extension\icons

REM 尝试安装图标生成依赖
pip install cairosvg Pillow >nul 2>&1

REM 运行图标转换脚本
if exist "convert_icons.py" (
    python convert_icons.py
) else (
    echo [WARNING] 图标转换脚本不存在
)

cd ..\..

REM 配置系统
echo [INFO] 配置系统...
if not exist "backend\config.json" (
    echo [INFO] 创建配置文件...
    copy backend\config.example.json backend\config.json
    echo [WARNING] 请编辑 backend\config.json 文件，填入您的配置信息：
    echo [WARNING]   - 小米账号和密码
    echo [WARNING]   - 小米Mimo API Key
    echo [WARNING]   - WebSocket端口等
) else (
    echo [SUCCESS] 配置文件已存在
)

REM 创建启动脚本
echo [INFO] 创建启动脚本...
echo @echo off > start.bat
echo echo 正在启动小爱音箱浏览器控制系统... >> start.bat
echo. >> start.bat
echo cd backend >> start.bat
echo call venv\Scripts\activate.bat >> start.bat
echo. >> start.bat
echo if not exist "config.json" ( >> start.bat
echo     echo 错误: 未找到配置文件 config.json >> start.bat
echo     echo 请复制 config.example.json 为 config.json 并填写配置 >> start.bat
echo     pause >> start.bat
echo     exit /b 1 >> start.bat
echo ) >> start.bat
echo. >> start.bat
echo echo 启动后端服务... >> start.bat
echo python main.py >> start.bat
echo. >> start.bat
echo pause >> start.bat

echo [SUCCESS] 启动脚本已创建: start.bat

REM 创建停止脚本
echo [INFO] 创建停止脚本...
echo @echo off > stop.bat
echo echo 正在停止小爱音箱浏览器控制系统... >> stop.bat
echo. >> stop.bat
echo taskkill /F /IM python.exe /FI "WINDOWTITLE eq main.py" >> stop.bat
echo. >> stop.bat
echo echo 服务已停止 >> stop.bat
echo. >> stop.bat
echo pause >> stop.bat

echo [SUCCESS] 停止脚本已创建: stop.bat

REM 创建快速入门指南
echo [INFO] 创建Windows快速入门指南...
echo # Windows快速入门指南 > QUICKSTART_WINDOWS.md
echo. >> QUICKSTART_WINDOWS.md
echo ## 1. 配置系统 >> QUICKSTART_WINDOWS.md
echo. >> QUICKSTART_WINDOWS.md
echo 编辑 `backend\config.json` 文件： >> QUICKSTART_WINDOWS.md
echo. >> QUICKSTART_WINDOWS.md
echo ```json >> QUICKSTART_WINDOWS.md
echo { >> QUICKSTART_WINDOWS.md
echo   "xiaomi": { >> QUICKSTART_WINDOWS.md
echo     "username": "您的小米账号", >> QUICKSTART_WINDOWS.md
echo     "password": "您的小米密码" >> QUICKSTART_WINDOWS.md
echo   }, >> QUICKSTART_WINDOWS.md
echo   "mimo_api": { >> QUICKSTART_WINDOWS.md
echo     "base_url": "https://api.xiaomimimo.com/v1", >> QUICKSTART_WINDOWS.md
echo     "api_key": "您的Mimo API Key", >> QUICKSTART_WINDOWS.md
echo     "model": "MiMo-V2-Flash" >> QUICKSTART_WINDOWS.md
echo   } >> QUICKSTART_WINDOWS.md
echo } >> QUICKSTART_WINDOWS.md
echo ``` >> QUICKSTART_WINDOWS.md
echo. >> QUICKSTART_WINDOWS.md
echo ## 2. 启动后端服务 >> QUICKSTART_WINDOWS.md
echo. >> QUICKSTART_WINDOWS.md
echo ```cmd >> QUICKSTART_WINDOWS.md
echo start.bat >> QUICKSTART_WINDOWS.md
echo ``` >> QUICKSTART_WINDOWS.md
echo. >> QUICKSTART_WINDOWS.md
echo ## 3. 安装浏览器插件 >> QUICKSTART_WINDOWS.md
echo. >> QUICKSTART_WINDOWS.md
echo 1. 打开Chrome浏览器 >> QUICKSTART_WINDOWS.md
echo 2. 访问 `chrome://extensions/` >> QUICKSTART_WINDOWS.md
echo 3. 开启"开发者模式" >> QUICKSTART_WINDOWS.md
echo 4. 点击"加载已解压的扩展程序" >> QUICKSTART_WINDOWS.md
echo 5. 选择 `browser_extension` 目录 >> QUICKSTART_WINDOWS.md
echo. >> QUICKSTART_WINDOWS.md
echo ## 4. 配置插件 >> QUICKSTART_WINDOWS.md
echo. >> QUICKSTART_WINDOWS.md
echo 1. 点击Chrome工具栏中的插件图标 >> QUICKSTART_WINDOWS.md
echo 2. 在"设置"标签页中配置WebSocket连接 >> QUICKSTART_WINDOWS.md
echo 3. 点击"连接"按钮 >> QUICKSTART_WINDOWS.md
echo. >> QUICKSTART_WINDOWS.md
echo ## 5. 测试系统 >> QUICKSTART_WINDOWS.md
echo. >> QUICKSTART_WINDOWS.md
echo 对小爱音箱说： >> QUICKSTART_WINDOWS.md
echo - "小爱同学，打开百度" >> QUICKSTART_WINDOWS.md
echo - "小爱同学，搜索最新新闻" >> QUICKSTART_WINDOWS.md
echo - "小爱同学，向下滚动" >> QUICKSTART_WINDOWS.md

echo [SUCCESS] Windows快速入门指南已创建: QUICKSTART_WINDOWS.md

echo.
echo ===========================================
echo [SUCCESS] Windows部署完成！
echo ===========================================
echo.
echo 下一步操作：
echo 1. 编辑 backend\config.json 文件
echo 2. 运行 start.bat 启动服务
echo 3. 安装Chrome浏览器插件
echo 4. 参考 QUICKSTART_WINDOWS.md 文件
echo.
pause