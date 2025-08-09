# 使用Python 3.9官方镜像作为基础镜像
FROM python:3.9

# 设置工作目录
WORKDIR /app

# 安装系统依赖（特别是mysqlclient需要的依赖）
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev \
        build-essential \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制项目代码到工作目录（包括README.md）
COPY . /app/

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露Django应用的端口
EXPOSE 8000

# 创建一个启动脚本，用于在容器启动时收集静态文件并启动应用
RUN echo '#!/bin/bash\npython manage.py collectstatic --noinput\ngunicorn --bind 0.0.0.0:8000 blog_drf.wsgi:application' > start.sh && chmod +x start.sh

# 启动应用
CMD ["./start.sh"]