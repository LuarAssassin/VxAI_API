from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .utils.serializers import SoftDeleteModelSerializer, DynamicFieldsModelSerializer
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from users.utils.sms import SMSUtil
import re
import uuid

User = get_user_model()

class UserSerializer(SoftDeleteModelSerializer, DynamicFieldsModelSerializer):
    """
    用户序列化器，用于用户信息的读取
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone', 'bio', 'avatar', 'created_at', 'updated_at', 'is_active', 'is_deleted', 'deleted_at']
        read_only_fields = ['created_at', 'updated_at', 'is_active', 'is_deleted', 'deleted_at']

class UserCreateSerializer(serializers.ModelSerializer):
    """
    用户创建序列化器，用于用户注册
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2', 'phone', 'bio']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "两次密码不匹配"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    用户更新序列化器，用于用户信息更新
    """
    class Meta:
        model = User
        fields = ['username', 'phone', 'bio', 'avatar']

class ChangePasswordSerializer(serializers.Serializer):
    """
    密码修改序列化器
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "两次新密码不匹配"})
        return attrs

class PhoneSerializer(serializers.Serializer):
    """
    手机号序列化器，用于发送验证码
    """
    phone = serializers.CharField(max_length=11, min_length=11)
    
    def validate_phone(self, value):
        """
        验证手机号格式
        """
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError(_("手机号格式不正确"))
        return value

class SMSVerificationSerializer(serializers.Serializer):
    """
    短信验证码序列化器，用于验证短信验证码
    """
    phone = serializers.CharField(max_length=11, min_length=11)
    code = serializers.CharField(max_length=6, min_length=6)
    
    def validate_phone(self, value):
        """
        验证手机号格式
        """
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError(_("手机号格式不正确"))
        return value
    
    def validate(self, attrs):
        """
        验证短信验证码
        """
        phone = attrs.get('phone')
        code = attrs.get('code')
        
        if not SMSUtil.verify_code(phone, code):
            raise serializers.ValidationError(_("验证码错误或已过期"))
        
        return attrs

class SMSLoginSerializer(SMSVerificationSerializer):
    """
    短信验证码登录序列化器
    """
    def validate(self, attrs):
        """
        验证短信验证码并返回用户信息和token
        """
        attrs = super().validate(attrs)
        phone = attrs.get('phone')
        
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            # 如果用户不存在，则创建一个新用户
            user = User.objects.create_user(
                phone=phone,
                username=str(uuid.uuid4())[:8],  # 使用UUID生成用户名
                password=None  # 不设置密码，只能通过短信验证码登录
            )
        
        # 生成JWT令牌
        refresh = RefreshToken.for_user(user)
        
        return {
            'user': user,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        } 