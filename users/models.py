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

class VisitorRecord(models.Model):
    """访客记录模型"""
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="用户",
        related_name="visitor_records"
    )  # 关联用户，允许为空
    ip_address = models.GenericIPAddressField(verbose_name="IP地址")
    user_agent = models.TextField(verbose_name="用户代理", blank=True, null=True)
    referer = models.URLField(verbose_name="来源页面", blank=True, null=True)
    path = models.CharField(max_length=500, verbose_name="访问路径")
    method = models.CharField(max_length=10, verbose_name="请求方法")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="访问时间")
    session_key = models.CharField(max_length=40, verbose_name="会话ID", blank=True, null=True)
    
    class Meta:
        verbose_name = "访客记录"
        verbose_name_plural = "访客记录"
        ordering = ['-timestamp']
        
    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.path} ({self.timestamp})"
        return f"{self.ip_address} - {self.path} ({self.timestamp})"
        
    @property
    def is_authenticated_user(self):
        """判断是否为已登录用户"""
        return self.user is not None