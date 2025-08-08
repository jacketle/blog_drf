from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    # 扩展Django自带的用户模型
    email = models.EmailField(unique=True)  # 邮箱，必须唯一
    nickname = models.CharField(max_length=100, blank=True, null=True)  # 昵称，可选
    avatar_file = models.ImageField(upload_to='avatars/', blank=True, null=True)  # 头像文件
    avatar_url = models.URLField(blank=True, null=True)  # 头像URL
    bio = models.TextField(blank=True, null=True)  # 个人简介
    is_station_master = models.BooleanField(default=False)  # 是否是站长
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
    updated_at = models.DateTimeField(auto_now=True)  # 更新时间

    def __str__(self):
        return self.username
    
    def get_post_count(self):
        """获取用户发布的文章数量"""
        return self.posts.count()
    
    def get_tag_count(self):
        """获取用户使用的不同标签数量"""
        # 获取用户所有文章的标签
        user_posts = self.posts.all()
        all_tags = []
        for post in user_posts:
            all_tags.extend(post.get_tags())
        # 返回不重复标签的数量
        return len(set(all_tags))