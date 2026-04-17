#!/bin/bash

# 小爱音箱 + 小米Mimo模型 + 浏览器控制系统 - 部署脚本

set -e

echo "=========================================="
echo "小爱音箱浏览器控制系统 - 自动部署脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python版本
check_python() {
    log_info "检查Python环境..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "未找到Python，请先安装Python 3.8+"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    log_success "找到Python版本: $PYTHON_VERSION"
    
    # 检查版本是否满足要求
    if [[ $(echo "$PYTHON_VERSION 3.8" | tr " " "\n" | sort -V | head -n1) != "3.8" ]]; then
        log_error "需要Python 3.8或更高版本，当前版本: $PYTHON_VERSION"
        exit 1
    fi
}

# 检查Chrome浏览器
check_chrome() {
    log_info "检查Chrome浏览器..."
    
    if command -v google-chrome &> /dev/null; then
        log_success "找到Chrome浏览器"
    elif command -v chromium-browser &> /dev/null; then
        log_success "找到Chromium浏览器"
    else
        log_warning "未找到Chrome/Chromium浏览器"
        log_warning "请确保已安装Chrome浏览器以使用浏览器插件"
    fi
}

# 安装Python依赖
install_python_deps() {
    log_info "安装Python依赖..."
    
    cd backend
    
    # 创建虚拟环境（如果不存在）
    if [ ! -d "venv" ]; then
        log_info "创建Python虚拟环境..."
        $PYTHON_CMD -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖
    log_info "安装项目依赖..."
    pip install -r requirements.txt
    
    log_success "Python依赖安装完成"
    
    cd ..
}

# 生成图标
generate_icons() {
    log_info "生成浏览器插件图标..."
    
    cd browser_extension/icons
    
    # 安装图标生成依赖
    $PYTHON_CMD -m pip install cairosvg Pillow 2>/dev/null || true
    
    # 运行图标转换脚本
    if [ -f "convert_icons.py" ]; then
        $PYTHON_CMD convert_icons.py
    else
        log_warning "图标转换脚本不存在，将使用占位图标"
    fi
    
    cd ../..
}

# 配置系统
configure_system() {
    log_info "配置系统..."
    
    # 检查配置文件
    if [ ! -f "backend/config.json" ]; then
        log_info "创建配置文件..."
        cp backend/config.example.json backend/config.json
        log_warning "请编辑 backend/config.json 文件，填入您的配置信息："
        log_warning "  - 小米账号和密码"
        log_warning "  - 小米Mimo API Key"
        log_warning "  - WebSocket端口等"
    else
        log_success "配置文件已存在"
    fi
}

# 创建启动脚本
create_start_script() {
    log_info "创建启动脚本..."
    
    cat > start.sh << 'EOF'
#!/bin/bash

# 小爱音箱浏览器控制系统 - 启动脚本

set -e

echo "正在启动小爱音箱浏览器控制系统..."

# 进入后端目录
cd backend

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "警告: 未找到虚拟环境，请先运行 setup.sh"
fi

# 检查配置文件
if [ ! -f "config.json" ]; then
    echo "错误: 未找到配置文件 config.json"
    echo "请复制 config.example.json 为 config.json 并填写配置"
    exit 1
fi

# 启动服务
echo "启动后端服务..."
python main.py

EOF
    
    chmod +x start.sh
    log_success "启动脚本已创建: start.sh"
}

# 创建停止脚本
create_stop_script() {
    log_info "创建停止脚本..."
    
    cat > stop.sh << 'EOF'
#!/bin/bash

# 小爱音箱浏览器控制系统 - 停止脚本

echo "正在停止小爱音箱浏览器控制系统..."

# 查找并停止Python进程
pkill -f "python.*main.py" || true

echo "服务已停止"

EOF
    
    chmod +x stop.sh
    log_success "停止脚本已创建: stop.sh"
}

# 创建README文件
create_readme() {
    log_info "创建快速入门指南..."
    
    cat > QUICKSTART.md << 'EOF'
# 快速入门指南

## 1. 配置系统

编辑 `backend/config.json` 文件：

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

## 2. 启动后端服务

```bash
./start.sh
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

### 问题1：对话记录获取失败
- 检查小米账号密码是否正确
- 确保小爱音箱已登录同一账号

### 问题2：AI解析失败
- 检查Mimo API Key是否有效
- 确保网络连接正常

### 问题3：插件连接失败
- 确保后端服务正在运行
- 检查WebSocket端口是否被占用

## 更多帮助

请参考项目根目录的 README.md 文件
EOF
    
    log_success "快速入门指南已创建: QUICKSTART.md"
}

# 主函数
main() {
    echo ""
    log_info "开始部署小爱音箱浏览器控制系统..."
    echo ""
    
    # 执行部署步骤
    check_python
    check_chrome
    install_python_deps
    generate_icons
    configure_system
    create_start_script
    create_stop_script
    create_readme
    
    echo ""
    log_success "=========================================="
    log_success "部署完成！"
    log_success "=========================================="
    echo ""
    log_info "下一步操作："
    log_info "1. 编辑 backend/config.json 文件"
    log_info "2. 运行 ./start.sh 启动服务"
    log_info "3. 安装Chrome浏览器插件"
    log_info "4. 参考 QUICKSTART.md 文件"
    echo ""
}

# 运行主函数
main