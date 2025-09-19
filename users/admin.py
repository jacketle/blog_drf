from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.forms.widgets import ClearableFileInput
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser, VisitorRecord

# 自定义widget，只支持文件上传
class ImageURLWidget(ClearableFileInput):
    def render(self, name, value, attrs=None, renderer=None):
        # 获取默认文件输入组件的HTML
        file_input = super().render(name, value, attrs, renderer)
        
        # 直接返回文件输入组件，不添加URL输入框
        return mark_safe(file_input)
    
    def value_from_datadict(self, data, files, name):
        """从表单数据中获取值"""
        # 使用默认的文件输入值
        return super().value_from_datadict(data, files, name)

# 自定义表单字段，支持URL输入
class ImageURLFormField(forms.Field):  # 修改为继承自forms.Field
    widget = ImageURLWidget
    
    def __init__(self, *args, **kwargs):
        self.url_validator = URLValidator()
        super().__init__(*args, **kwargs)
    
    def to_python(self, value):
        """允许URL字符串通过验证"""
        if not value:
            return None
        
        # 如果是URL，直接返回
        if isinstance(value, str) and value.startswith(('http://', 'https://')):
            # 验证URL格式
            try:
                self.url_validator(value)
                return value
            except ValidationError:
                raise ValidationError('请输入有效的URL地址')
            
        # 否则使用默认的文件处理
        return super().to_python(value)
    
    def validate(self, value):
        """验证值"""
        # 调用父类验证
        super().validate(value)
        
        # 如果有值但不是文件也不是URL，则报错
        if value and not isinstance(value, str):
            # 对于文件对象，使用图像字段的验证
            if hasattr(value, 'content_type'):
                # 这里可以添加文件类型验证
                pass

# 自定义用户管理表单
class CustomUserAdminForm(forms.ModelForm):
    avatar_file = ImageURLFormField(required=False)
    avatar_url = forms.URLField(required=False)
    
    class Meta:
        model = CustomUser
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 如果是编辑现有用户，且avatar是URL，则设置初始值
        if self.instance and self.instance.avatar_url:
            if isinstance(self.instance.avatar_url, str) and self.instance.avatar_url.startswith(('http://', 'https://')):
                self.fields['avatar_url'].widget.attrs['data-url'] = self.instance.avatar_url

# 自定义用户管理界面
class CustomUserAdmin(UserAdmin):
    form = CustomUserAdminForm  # 使用自定义表单
    
    # 列表显示字段
    list_display = ('username', 'email', 'nickname', 'is_station_master', 'is_staff', 'is_active')
    list_filter = ('is_station_master', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'nickname')
    ordering = ('-date_joined',)
    
    # 详情页字段分组
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('email', 'nickname', 'avatar_file', 'avatar_url', 'bio')}),
        ('权限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_station_master', 'groups', 'user_permissions')}),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )
    
    # 创建用户时的字段
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'nickname', 'is_station_master', 'is_active', 'is_staff')}
        ),
    )

# 访客记录管理界面
class VisitorRecordAdmin(admin.ModelAdmin):
    # 列表显示字段
    list_display = ('get_user_display', 'ip_address', 'path', 'method', 'timestamp', 'is_authenticated_user_display')
    list_filter = ('method', 'timestamp', 'user')
    search_fields = ('ip_address', 'path', 'user_agent', 'user__username')
    ordering = ('-timestamp',)
    
    # 只读字段
    readonly_fields = ('user', 'ip_address', 'user_agent', 'referer', 'path', 'method', 'timestamp', 'session_key', 'is_authenticated_user_display')
    
    # 详情页字段分组
    fieldsets = (
        ('用户信息', {
            'fields': ('user', 'is_authenticated_user_display')
        }),
        ('访问信息', {
            'fields': ('ip_address', 'path', 'method', 'timestamp')
        }),
        ('详细信息', {
            'fields': ('user_agent', 'referer', 'session_key')
        }),
    )
    
    # 设置每页显示数量
    list_per_page = 20
    
    # 添加日期层级筛选
    # date_hierarchy = 'timestamp'
    
    def get_urls(self):
        """添加自定义URL"""
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_site.admin_view(self.analytics_view), name='users_visitorrecord_analytics'),
            path('api/analytics/daily-visits/', self.admin_site.admin_view(self.daily_visits_data), name='users_visitorrecord_daily_visits_data'),
            path('api/analytics/post-rankings/', self.admin_site.admin_view(self.post_rankings_data), name='users_visitorrecord_post_rankings_data'),
        ]
        
        # 打印注册的URL用于调试
        print("注册的自定义URL:")
        for url in custom_urls:
            print(f"  - {url.pattern}")
        
        return custom_urls + urls
    
    def analytics_view(self, request):
        """数据分析页面视图"""
        context = dict(
            self.admin_site.each_context(request),
            title="数据分析",
        )
        return render(request, 'admin/analytics.html', context)
    
    def daily_visits_data(self, request):
        """每日访问量数据API"""
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta, datetime
        
        # 计算最近7天的日期
        today = timezone.now().date()
        dates = []
        date_range = []
        
        for i in range(6, -1, -1):  # 从6天前到今天
            date = today - timedelta(days=i)
            dates.append(date.strftime('%m-%d'))
            date_range.append(date)
        
        # 获取所有访客记录数量
        total_records = VisitorRecord.objects.count()
        
        # 打印调试信息
        print(f"总访客记录数: {total_records}")
        print(f"查询日期范围: {date_range[0]} 到 {date_range[-1]}")
        
        # 如果没有记录，返回空数据
        if total_records == 0:
            return JsonResponse({
                'dates': dates,
                'counts': [0] * len(dates)
            })
        
        # 查询每日访问量数据
        # 使用更准确的日期范围查询
        daily_visits = VisitorRecord.objects.extra(
            select={'visit_date': 'DATE(timestamp)'}
        ).values('visit_date').annotate(
            count=Count('id')
        ).order_by('visit_date')
        
        # 打印查询结果
        print(f"查询结果: {list(daily_visits)}")
        
        # 构造图表数据
        counts = []
        visit_dict = {}
        
        # 将查询结果转换为字典，键为日期字符串
        for visit in daily_visits:
            if isinstance(visit['visit_date'], str):
                date_key = visit['visit_date']
            else:
                date_key = visit['visit_date'].strftime('%Y-%m-%d')
            visit_dict[date_key] = visit['count']
        
        # 为每个日期查找对应的访问量
        for date in date_range:
            date_key = date.strftime('%Y-%m-%d')
            counts.append(visit_dict.get(date_key, 0))
        
        print(f"返回数据: dates={dates}, counts={counts}")
        
        return JsonResponse({
            'dates': dates,
            'counts': counts
        })
    
    def post_rankings_data(self, request):
        """帖子访问排行数据API"""
        from django.db.models import Count, Q
        from posts.models import Post
        
        # 获取所有访客记录数量
        total_records = VisitorRecord.objects.count()
        
        # 打印调试信息
        print(f"总访客记录数: {total_records}")
        
        # 如果没有记录，返回空数据
        if total_records == 0:
            return JsonResponse({
                'paths': [],
                'counts': [],
                'titles': []  # 添加标题字段
            })
        
        # 先查看一些访客记录的路径格式，用于调试
        sample_paths = VisitorRecord.objects.values('path').distinct()[:10]
        print(f"示例路径: {[p['path'] for p in sample_paths]}")
        
        # 查找具体的帖子详情页访问记录
        # 帖子详情页的URL模式是: /api/posts/{slug}/
        post_detail_visits = VisitorRecord.objects.filter(
            path__regex=r'^/api/posts/[^/]+/$'  # 匹配 /api/posts/slug/ 格式
        ).values('path').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # 如果没有找到具体的帖子详情页访问记录，尝试其他模式
        if not post_detail_visits:
            post_detail_visits = VisitorRecord.objects.filter(
                Q(path__startswith='/api/posts/') & 
                ~Q(path='/api/posts/') &  # 排除列表页
                ~Q(path__endswith='/update/') &  # 排除更新页
                ~Q(path__endswith='/delete/') &  # 排除删除页
                ~Q(path__endswith='/preview/')   # 排除预览页
            ).values('path').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
        
        # 打印查询结果
        print(f"帖子详情页访问排行查询结果: {list(post_detail_visits)}")
        
        # 提取数据
        paths = [visit['path'] for visit in post_detail_visits]
        counts = [visit['count'] for visit in post_detail_visits]
        
        # 获取对应的帖子标题
        titles = []
        for path in paths:
            # 从路径中提取slug: /api/posts/{slug}/ -> {slug}
            parts = path.strip('/').split('/')
            if len(parts) >= 3 and parts[0] == 'api' and parts[1] == 'posts':
                slug = parts[2]
                try:
                    post = Post.objects.get(slug=slug)
                    titles.append(post.title)
                except Post.DoesNotExist:
                    titles.append(f"未知帖子 ({slug})")
            else:
                titles.append("未知帖子")
        
        # 如果没有数据，返回空数组而不是None
        if not paths and not counts:
            paths = []
            counts = []
            titles = []
        
        print(f"返回数据: paths={paths}, counts={counts}, titles={titles}")
        
        return JsonResponse({
            'paths': paths,
            'counts': counts,
            'titles': titles  # 返回帖子标题
        })
    
    def get_user_display(self, obj):
        """显示用户信息"""
        if obj.user:
            return obj.user.username
        return "未登录用户"
    get_user_display.short_description = "用户"
    get_user_display.admin_order_field = 'user__username'
    
    # 修改方法名为is_authenticated_user_display以匹配其他地方的引用
    def is_authenticated_user_display(self, obj):
        """显示是否为已登录用户"""
        return obj.user is not None  # 返回布尔值
    is_authenticated_user_display.short_description = "是否登录"
    is_authenticated_user_display.boolean = True

# 注册模型
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(VisitorRecord, VisitorRecordAdmin)