from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .utils.serializers import SoftDeleteModelSerializer, DynamicFieldsModelSerializer

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