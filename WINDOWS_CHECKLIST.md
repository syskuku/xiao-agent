# Windows部署检查清单

## 📋 部署前检查

### ✅ 必需软件
- [ ] Python 3.8+ 已安装（检查：`python --version`）
- [ ] Chrome浏览器 已安装
- [ ] 项目文件已下载到Windows电脑

### ✅ 必需信息
- [ ] 小米账号和密码
- [ ] 小米Mimo API Key（从 platform.xiaomimimo.com 获取）
- [ ] 小爱音箱设备已登录同一小米账号

## 🚀 部署步骤检查

### ✅ 步骤1：运行部署脚本
```cmd
:: 打开CMD，进入项目目录
cd xiaomi_mimo_browser_control

:: 运行Windows部署脚本
scripts\setup.bat
```
- [ ] 部署脚本运行成功
- [ ] 无错误信息
- [ ] 虚拟环境创建成功
- [ ] 依赖安装成功

### ✅ 步骤2：配置系统
```cmd
:: 编辑配置文件
notepad backend\config.json
```
- [ ] 配置文件已创建
- [ ] 小米账号已填写
- [ ] 小米密码已填写
- [ ] Mimo API Key已填写
- [ ] WebSocket配置正确

### ✅ 步骤3：启动服务
```cmd
:: 启动后端服务
start.bat
```
- [ ] 服务启动成功
- [ ] 无错误信息
- [ ] 显示"系统启动完成，等待语音指令..."

### ✅ 步骤4：安装Chrome插件
1. [ ] 打开Chrome浏览器
2. [ ] 访问 `chrome://extensions/`
3. [ ] 开启"开发者模式"
4. [ ] 点击"加载已解压的扩展程序"
5. [ ] 选择 `browser_extension` 目录
6. [ ] 插件安装成功

### ✅ 步骤5：配置插件连接
1. [ ] 点击Chrome工具栏中的插件图标
2. [ ] 在"设置"标签页中配置：
   - 主机地址：`localhost`
   - 端口：`8765`
3. [ ] 点击"连接"按钮
4. [ ] 状态显示"已连接"

### ✅ 步骤6：测试系统
1. [ ] 对小爱音箱说："小爱同学，打开百度"
2. [ ] 浏览器自动打开百度页面
3. [ ] 查看插件日志，确认操作成功

## 🔧 故障排除检查

### ✅ Python问题
- [ ] Python已添加到PATH环境变量
- [ ] 虚拟环境激活成功
- [ ] 依赖安装无错误

### ✅ 网络问题
- [ ] 能访问小米API
- [ ] 能访问Mimo API
- [ ] 端口8765未被占用

### ✅ 权限问题
- [ ] 对项目目录有读写权限
- [ ] 防火墙未阻止Python
- [ ] 杀毒软件未阻止脚本

## 📁 文件检查

### ✅ 必需文件存在
- [ ] `backend/main.py`
- [ ] `backend/conversation.py`
- [ ] `backend/ai_parser.py`
- [ ] `backend/websocket_server.py`
- [ ] `backend/config.json`
- [ ] `browser_extension/manifest.json`
- [ ] `browser_extension/background.js`
- [ ] `browser_extension/content.js`
- [ ] `scripts/setup.bat`
- [ ] `start.bat`

### ✅ 文档文件存在
- [ ] `README.md`
- [ ] `WINDOWS_DEPLOYMENT.md`
- [ ] `QUICKSTART_WINDOWS.md`（部署脚本生成）

## 🎯 功能测试

### ✅ 基础功能测试
- [ ] 打开网页：`"小爱同学，打开百度"`
- [ ] 搜索内容：`"小爱同学，搜索新闻"`
- [ ] 页面操作：`"小爱同学，向下滚动"`

### ✅ 高级功能测试
- [ ] 元素点击：`"小爱同学，点击搜索按钮"`
- [ ] 文本输入：`"小爱同学，输入搜索关键词"`
- [ ] 数据提取：`"小爱同学，提取页面数据"`

## 📞 获取帮助

如果遇到问题：
1. [ ] 查看 `WINDOWS_DEPLOYMENT.md` 文件
2. [ ] 查看 `QUICKSTART_WINDOWS.md` 文件
3. [ ] 检查系统日志：`backend\system.log`
4. [ ] 查看插件日志：Chrome插件弹出窗口

## 🎉 部署完成确认

- [ ] 所有步骤完成
- [ ] 系统运行正常
- [ ] 语音指令测试成功
- [ ] 浏览器操作正常

**恭喜！Windows部署完成！** 🎉