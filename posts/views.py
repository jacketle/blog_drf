from django.shortcuts import render
from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Post
from .serializers import PostListSerializer, PostDetailSerializer, PostCreateSerializer, PostUpdateSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.


class PostListView(generics.ListAPIView):
    """帖子列表视图"""
    serializer_class = PostListSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author', 'is_published', 'category']
    search_fields = ['title', 'content', 'tags']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    @swagger_auto_schema(
        operation_summary="获取帖子列表",
        operation_description="返回所有已发布的帖子列表，支持分页、过滤、搜索和排序。管理员可以看到所有帖子（包括草稿）",
        manual_parameters=[
            openapi.Parameter('author', openapi.IN_QUERY, description="根据作者ID过滤", type=openapi.TYPE_INTEGER),
            openapi.Parameter('is_published', openapi.IN_QUERY, description="根据发布状态过滤", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('category', openapi.IN_QUERY, description="根据分区过滤(tech:技术, chat:杂谈, life:生活)", type=openapi.TYPE_STRING),
            openapi.Parameter('search', openapi.IN_QUERY, description="搜索标题、内容或标签", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="排序字段，支持created_at和updated_at", type=openapi.TYPE_STRING),
        ],
        responses={200: PostListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    # 修复：正确缩进 get_queryset() 方法
    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.all()
        
        if user.is_authenticated:
            # 作者能看到自己的所有帖子 + 其他人的已发布帖子
            queryset = queryset.filter(
                Q(author=user) | Q(is_published=True)
            )
        else:
            # 未登录用户只能看到已发布帖子
            queryset = queryset.filter(is_published=True)
        
        return queryset


class PostDetailView(generics.RetrieveAPIView):
    """帖子详情视图"""
    serializer_class = PostDetailSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'slug'
    
    @swagger_auto_schema(
        operation_summary="获取帖子详情",
        operation_description="根据slug获取单个帖子的详细信息。只有作者或管理员可以查看未发布的帖子",
        responses={200: PostDetailSerializer}
    )
    def get(self, request, *args, **kwargs):
        """处理GET请求，返回帖子详情，并自动增加点击数"""
        # 获取帖子对象
        post = self.get_object()
        # 增加点击数
        post.click_count += 1
        post.save(update_fields=['click_count'])
        # 继续原来的逻辑返回帖子详情
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        """返回已发布的帖子，作者可以看到自己的草稿"""
        user = self.request.user
        queryset = Post.objects.all()
        
        # 非管理员用户和非作者只能看到已发布的帖子
        if not (user.is_authenticated and (user.is_staff or 
                queryset.filter(slug=self.kwargs.get(self.lookup_field), author=user).exists())):
            queryset = queryset.filter(is_published=True)
            
        return queryset


class PostCreateView(generics.CreateAPIView):
    """创建帖子视图"""
    serializer_class = PostCreateSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    @swagger_auto_schema(
        operation_summary="创建新帖子",
        operation_description="创建一个新的帖子，需要认证用户权限。作者会自动设置为当前用户",
        request_body=PostCreateSerializer,
        responses={201: PostDetailSerializer}
    )
    def post(self, request, *args, **kwargs):
        """处理POST请求，创建新帖子"""
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """保存时自动设置作者"""
        serializer.save(author=self.request.user)


class PostUpdateView(generics.UpdateAPIView):
    """更新帖子视图"""
    serializer_class = PostUpdateSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'slug'
    
    @swagger_auto_schema(
        operation_summary="更新帖子",
        operation_description="更新指定slug的帖子，只有作者或管理员可以更新帖子",
        request_body=PostUpdateSerializer,
        responses={200: PostDetailSerializer}
    )
    def put(self, request, *args, **kwargs):
        """处理PUT请求，更新帖子"""
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="部分更新帖子",
        operation_description="部分更新指定slug的帖子，只有作者或管理员可以更新帖子",
        request_body=PostUpdateSerializer,
        responses={200: PostDetailSerializer}
    )
    def patch(self, request, *args, **kwargs):
        """处理PATCH请求，部分更新帖子"""
        return super().patch(request, *args, **kwargs)
    
    def get_queryset(self):
        """只允许作者或管理员更新帖子"""
        user = self.request.user
        queryset = Post.objects.all()
        
        # 只有作者或管理员可以更新帖子
        if user.is_staff:
            return queryset
        return queryset.filter(author=user)


class PostDeleteView(generics.DestroyAPIView):
    """删除帖子视图"""
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'slug'
    
    @swagger_auto_schema(
        operation_summary="删除帖子",
        operation_description="删除指定slug的帖子，只有作者或管理员可以删除帖子",
        responses={204: 'No Content'}
    )
    def delete(self, request, *args, **kwargs):
        """处理DELETE请求，删除帖子"""
        return super().delete(request, *args, **kwargs)
    
    def get_queryset(self):
        """只允许作者或管理员删除帖子"""
        user = self.request.user
        queryset = Post.objects.all()
        
        # 只有作者或管理员可以删除帖子
        if user.is_staff:
            return queryset
        return queryset.filter(author=user)


class PostPreviewView(generics.RetrieveAPIView):
    """帖子预览视图（仅作者和管理员可访问）"""
    serializer_class = PostDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'slug'
    
    @swagger_auto_schema(
        operation_summary="预览帖子",
        operation_description="预览指定slug的帖子，仅作者或管理员可以访问此接口",
        responses={200: PostDetailSerializer}
    )
    def get(self, request, *args, **kwargs):
        """处理GET请求，预览帖子"""
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        """只允许作者或管理员预览帖子"""
        user = self.request.user
        queryset = Post.objects.all()
        
        # 只有作者或管理员可以预览帖子
        if user.is_staff:
            return queryset
        return queryset.filter(author=user)

