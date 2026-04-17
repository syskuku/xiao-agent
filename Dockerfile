# 小爱音箱 + 小米Mimo模型 + 浏览器控制系统 - Dockerfile
# 基于Python 3.9 slim镜像

FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY backend/ ./backend/
COPY browser_extension/ ./browser_extension/
COPY scripts/ ./scripts/

# 安装Python依赖
RUN pip install --no-cache-dir -r backend/requirements.txt

# 创建配置文件目录
RUN mkdir -p /app/conf

# 创建日志目录
RUN mkdir -p /app/logs

# 复制配置文件模板（如果不存在）
RUN cp backend/config.example.json backend/config.json 2>/dev/null || true

# 暴露端口
EXPOSE 8765

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(1); result = s.connect_ex(('localhost', 8765)); s.close(); exit(result)"

# 启动命令
CMD ["python", "backend/main.py"]