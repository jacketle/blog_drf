import datetime
import re  # 添加缺失的re模块导入
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import VisitorRecord, CustomUser

class VisitorTrackingMiddleware(MiddlewareMixin):
    """
    记录访客信息的中间件
    """
    
    # 排除不需要记录的路径模式
    EXCLUDED_PATTERNS = [
        r'^/admin/',  # Django admin
        r'^/static/',  # 静态文件
        r'^/media/',   # 媒体文件
        r'^/favicon\.ico$',
        r'^/robots\.txt$',
    ]
    
    def should_exclude(self, path):
        """判断是否应该排除该路径"""
        for pattern in self.EXCLUDED_PATTERNS:
            if re.match(pattern, path):
                return True
        return False
    
    def process_request(self, request):
        """在处理请求前记录访客信息"""
        # 检查是否应该排除该路径
        if self.should_exclude(request.path):
            return None
            
        # 获取访客信息
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referer = request.META.get('HTTP_REFERER', '')
        session_key = request.session.session_key
        
        # 获取用户信息（如果已登录）
        user = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            
        # 使用Django的timezone.now()获取当前时间，确保有时区信息
        current_time = timezone.now()
        
        # 创建访客记录
        VisitorRecord.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer,
            path=request.path,
            method=request.method,
            session_key=session_key,
            timestamp=current_time  # 使用正确的当前时间
        )
        
        return None
    
    def get_client_ip(self, request):
        """获取客户端真实IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip