from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

# 自定义字段，用于处理头像URL
class AvatarField(serializers.ImageField):
    def to_representation(self, value):
        """将字段值转换为JSON可序列化的形式"""
        # 如果值是字符串（URL），直接返回
        if isinstance(value, str):
            # 如果是完整的URL（http或https），直接返回
            if value.startswith(('http://', 'https://')):
                return value
            # 如果是相对路径，构造完整URL
            elif value:
                # 注意：这里假设MEDIA_URL是 '/media/'，实际项目中应从settings获取
                return f'/media/{value}'
        # 如果值存在但不是字符串，使用父类的处理方式
        if value:
            return super().to_representation(value)
        # 如果值为空，返回None
        return None

# 自定义字段，用于处理头像文件和URL
class AvatarFileField(serializers.ImageField):
    def to_representation(self, value):
        """将字段值转换为JSON可序列化的形式"""
        if value:
            return super().to_representation(value)
        return None

class UserRegistrationSerializer(serializers.ModelSerializer):
    # 注册序列化器
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'nickname')
        extra_kwargs = {
            'email': {'required': True},
            'nickname': {'required': False}
        }

    def validate(self, attrs):
        # 验证两次密码是否一致
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "两次输入的密码不一致"
            })
        return attrs

    def create(self, validated_data):
        # 创建用户
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user




class UserDetailSerializer(serializers.ModelSerializer):
    # 使用自定义的头像字段
    avatar_file = AvatarFileField(required=False)
    avatar_url = serializers.URLField(required=False)
    post_count = serializers.SerializerMethodField()
    tag_count = serializers.SerializerMethodField()
    
    # 用户详情序列化器
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'nickname', 'avatar_file', 'avatar_url', 'bio', 'is_station_master', 'date_joined', 'post_count', 'tag_count')
        read_only_fields = ('id', 'email', 'date_joined', 'is_station_master', 'post_count', 'tag_count')
    
    def get_post_count(self, obj) -> int:  # 添加类型提示
        """获取用户发布的文章数量"""
        return obj.get_post_count()
    
    def get_tag_count(self, obj) -> int:  # 添加类型提示
        """获取用户使用的不同标签数量"""
        return obj.get_tag_count()


class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器，包含统计信息"""
    post_count = serializers.SerializerMethodField()
    tag_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nickname', 'avatar_url', 'bio', 
                  'is_station_master', 'created_at', 'updated_at', 'post_count', 'tag_count']
        read_only_fields = ['id', 'username', 'email', 'created_at', 'updated_at', 'post_count', 'tag_count']
    
    def get_post_count(self, obj) -> int:  # 添加类型提示
        """获取用户发布的文章数量"""
        return obj.get_post_count()
    
    def get_tag_count(self, obj) -> int:  # 添加类型提示
        """获取用户使用的不同标签数量"""
        return obj.get_tag_count()