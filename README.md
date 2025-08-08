# Blog_drf项目

Backend_Blog_Drf主要是一个基于Djang和Django REST Framework构建的个人博客论坛后端项目。主要功能有登录注册，markdown文章发布，可以嵌入B站视频，网易云音乐，编辑文章，后台管理等，并且支持RESTful API接口。

## 技术栈

- Python 3.x
- Django 4.2.23
- Django REST Framework
- MySQL 8.0+
- Redis
- SimpleUI (Django管理后台)
- djangorestframework-simplejwt (JWT认证)
- Pillow (图像处理)
- django-cors-headers (跨域支持)
- drf-yasg (API文档)

## 项目结构

```
blog_drf/
├── blog_drf/          # 项目主目录
│   ├── settings.py    # 项目配置文件
│   ├── urls.py        # 主路由配置
│   └── wsgi.py        # WSGI配置
├── users/             # 用户应用
├── posts/             # 文章应用
├── manage.py          # Django管理脚本
├── requirements.txt   # 项目依赖
└── .env              # 环境变量配置文件
```

## 安装步骤

1.将项目下载到本地

2.激活python环境并安装依赖

3.配置环境变量 .env,输入自己的数据库信息

4.数据库迁移和超级用户(可选)

5.运行项目进入Swagger UI: http://127.0.0.1:8000/swagger/可查询接口

