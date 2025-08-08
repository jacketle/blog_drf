from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.forms.widgets import ClearableFileInput
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from .models import CustomUser

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

# 注册模型
admin.site.register(CustomUser, CustomUserAdmin)