# 使用官方Python镜像作为基础镜像
FROM python:3.9-slim

# 设置时区为中国时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 设置工作目录
WORKDIR /app/src

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# 更新apt源为中国镜像并安装必要的包
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list \
    && sed -i 's/security.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        tzdata \
    && rm -rf /var/lib/apt/lists/*

# 配置pip使用国内源，并升级pip
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install --no-cache-dir --upgrade pip

# 复制requirements.txt
COPY requirements.txt /app/

# 安装Python依赖
RUN pip install --no-cache-dir -r /app/requirements.txt --timeout 1000

# 复制项目文件
COPY src/ .

# 暴露端口
EXPOSE 5555

# 启动命令
CMD ["python", "app.py"] 