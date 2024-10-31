# 使用Python 3.9作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

# 替换为国内源并安装系统依赖
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list \
    && sed -i 's/security.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 配置pip使用国内源，并升级pip
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install --no-cache-dir --upgrade pip

# 复制requirements.txt
COPY requirements.txt .

# 安装Python依赖（添加超时设置）
RUN pip install --no-cache-dir -r requirements.txt --timeout 1000

# 复制项目文件
COPY src/ ./src/

# 暴露端口
EXPOSE 5555

# 启动命令
CMD ["python", "src/app.py"] 