from rest_framework import serializers
from .models import Post
from django.contrib.auth import get_user_model
import markdown
from bs4 import BeautifulSoup
User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    """作者序列化器"""
    post_count = serializers.SerializerMethodField()
    tag_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'nickname', 'bio', 'post_count', 'tag_count', 'avatar_url', 'is_station_master')
    
    def get_post_count(self, obj):
        """获取用户发布的文章数量"""
        return obj.get_post_count()
    
    def get_tag_count(self, obj):
        """获取用户使用的不同标签数量"""
        return obj.get_tag_count()


class PostListSerializer(serializers.ModelSerializer):
    """帖子列表序列化器"""
    author = AuthorSerializer(read_only=True)
    tag_list = serializers.SerializerMethodField()
    content_summary = serializers.SerializerMethodField()  # 添加摘要字段
    
    class Meta:
        model = Post
        fields = ('id', 'title', 'cover_image_url', 'slug', 'created_at', 'author', 'tag_list', 'is_published', 'category', 'content_summary', 'click_count')  # 添加click_count字段
    
    def get_tag_list(self, obj):
        """返回标签列表"""
        return obj.get_tags()
        
    def get_content_summary(self, obj):
        """生成Markdown格式的内容摘要
        保留基本格式，移除图片和代码块，限制长度约200个字符
        """
        # 解析Markdown为HTML
        html_content = markdown.markdown(obj.content)
        
        # 使用BeautifulSoup处理HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 移除图片
        for img in soup.find_all('img'):
            img.decompose()
        
        # 移除代码块
        for code_block in soup.find_all('pre'):
            code_block.decompose()
        
        # 获取文本内容
        text_content = soup.get_text()
        
        # 限制长度并确保在句子结束处截断
        max_length = 200
        if len(text_content) <= max_length:
            return text_content
        
        # 找到最近的句子结束处
        truncate_pos = text_content.rfind('.', 0, max_length)
        if truncate_pos == -1:
            truncate_pos = text_content.rfind('。', 0, max_length)
        if truncate_pos == -1:
            truncate_pos = max_length
        
        return text_content[:truncate_pos + 1] + '...'


class PostDetailSerializer(serializers.ModelSerializer):
    """帖子详情序列化器"""
    author = AuthorSerializer(read_only=True)
    tag_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ('author', 'created_at', 'updated_at', 'click_count')  # 添加click_count到只读字段
    
    def get_tag_list(self, obj):
        """返回标签列表"""
        return obj.get_tags()


class PostCreateSerializer(serializers.ModelSerializer):
    """帖子创建序列化器"""
    # 添加 is_published 字段，默认为 True 表示创建即发布
    is_published = serializers.BooleanField(default=True)
    
    class Meta:
        model = Post
        fields = ('title', 'cover_image_url', 'content', 'tags', 'category', 'slug', 'is_published')
        
    # def create(self, validated_data):
    #     """创建帖子时自动设置作者为当前用户"""
    #     # 从上下文中获取当前用户
    #     user = self.context['request'].user
    #     # 创建帖子并设置作者
    #     post = Post.objects.create(author=user, **validated_data)
    #     return post


class PostUpdateSerializer(serializers.ModelSerializer):
    """帖子更新序列化器"""
    class Meta:
        model = Post
        fields = ('title', 'cover_image_url', 'content', 'tags', 'category', 'slug', 'is_published')