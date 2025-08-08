from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import UserRegistrationView, UserDetailView, UserPublicProfileView, UserStatisticsView 

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),  # 注册
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # 获取令牌
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # 刷新令牌
    path('profile/', UserDetailView.as_view(), name='user_profile'),  # 个人资料
    path('profile/<str:username>/', UserPublicProfileView.as_view(), name='user_public_profile'),  # 公开资料
    path('profile/<str:username>/statistics/', UserStatisticsView.as_view(), name='user_statistics'),  # 用户统计数据

]