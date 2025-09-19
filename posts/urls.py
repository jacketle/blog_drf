from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post-list'),
    path('create/', views.PostCreateView.as_view(), name='post-create'),  # 移到前面
    path('<slug:slug>/', views.PostDetailView.as_view(), name='post-detail'),  # 移到后面
    path('<slug:slug>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('<slug:slug>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    path('<slug:slug>/preview/', views.PostPreviewView.as_view(), name='post-preview'),
   
]