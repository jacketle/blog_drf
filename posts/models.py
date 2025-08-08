from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone

# Create your models here.

class Post(models.Model):
    # 定义分区选项
    CATEGORY_CHOICES = [
        ('tech', '技术'),
        ('chat', '杂谈'),
        ('life', '生活'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="标题")
    cover_image_url = models.URLField(blank=True, null=True, verbose_name="帖子封面图片URL")
    content = models.TextField(verbose_name="Markdown内容")
    tags = models.CharField(max_length=200, blank=True, null=True, verbose_name="标签（逗号分隔）")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='tech', verbose_name="分区")
    slug = models.SlugField(max_length=200, blank=True, null=True, unique=True, verbose_name="自定义链接slug")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="帖子发布时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="帖子修改时间")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts', verbose_name="帖子作者")
    
    # 用于预览的字段
    is_published = models.BooleanField(default=False, verbose_name="是否发布")
    
    # 添加点击数字段
    click_count = models.PositiveIntegerField(default=0, verbose_name="点击数")

    class Meta:
        verbose_name = "帖子"
        verbose_name_plural = "帖子"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # 如果没有提供slug，则根据标题自动生成
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)
    
    def get_tags(self):
        """返回标签列表"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []