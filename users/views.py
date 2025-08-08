from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, UserDetailSerializer, UserSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    """
    用户注册接口
    创建新用户账号，需要提供用户名、邮箱、密码和确认密码
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    用户个人资料接口
    获取或更新当前登录用户的个人资料信息
    """
    serializer_class = UserDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserPublicProfileView(generics.RetrieveAPIView):
    """
    用户公开资料接口
    获取指定用户的公开资料信息，无需登录
    """
    serializer_class = UserDetailSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'username'
    queryset = User.objects.all()

class UserStatisticsView(generics.RetrieveAPIView):
    """
    用户统计数据接口
    获取指定用户的统计数据信息，包括文章数量、标签数量等
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'username'
    queryset = User.objects.all()
    
    @swagger_auto_schema(
        operation_summary="获取用户统计数据",
        operation_description="获取指定用户的统计数据信息，包括文章数量、标签数量等",
        responses={200: UserSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)