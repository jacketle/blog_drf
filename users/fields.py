from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
class ImageURLField(models.ImageField):
    """自定义字段，支持图片上传和外部URL"""
    
    def __init__(self, *args, **kwargs):
        # 为URL验证器设置参数
        self.url_validator = URLValidator()
        super().__init__(*args, **kwargs)
    
    def to_python(self, value):
        """将输入值转换为Python对象"""
        # 如果值为空，直接返回
        if not value:
            return value
        
        # 尝试验证是否为URL
        try:
            self.url_validator(value)
            # 如果是有效的URL，直接返回
            return value
        except ValidationError:
            # 如果不是有效的URL，使用父类的处理方式（文件上传）
            return super().to_python(value)
    
    def pre_save(self, model_instance, add):
        """在保存前的处理"""
        # 获取字段值
        file = getattr(model_instance, self.attname)
        
        # 如果值是URL，不进行文件上传处理
        if isinstance(file, str) and file.startswith(('http://', 'https://')):
            return file
        
        # 否则使用父类的文件上传处理
        return super().pre_save(model_instance, add)