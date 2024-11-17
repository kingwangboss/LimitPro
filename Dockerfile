# 使用Python 3.11.0作为基础镜像
FROM python:3.11.0-slim

# 设置pip镜像源参数
ARG PYPI_MIRROR=https://pypi.tuna.tsinghua.edu.cn/simple

# 设置工作目录
WORKDIR /app

# 设置pip镜像源
RUN pip config set global.index-url ${PYPI_MIRROR}

# 复制项目文件
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建日志目录
RUN mkdir -p logs

# 设置环境变量
ENV PYTHONPATH=/app
ENV TZ=Asia/Shanghai

# 设置时区
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 暴露端口
EXPOSE 5001