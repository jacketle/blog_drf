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

# 复制项目依赖文件到工作目录
COPY requirements.txt /app/

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码到工作目录
COPY . /app/

# 暴露Django应用的端口
EXPOSE 8000

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 启动应用
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "blog_drf.wsgi:application"]