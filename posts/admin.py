from django.contrib import admin
from django.utils.html import format_html
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'cover_image_thumbnail', 'author', 'is_published', 'created_at')  # 添加封面图列
    list_filter = ('is_published', 'created_at', 'author', 'category')  # 添加分区筛选
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-created_at',)
    
    # 封面图片显示方法
    def cover_image_thumbnail(self, obj):
        if obj.cover_image_url:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.cover_image_url)
        return '无图片'
    cover_image_thumbnail.short_description = '封面图片'