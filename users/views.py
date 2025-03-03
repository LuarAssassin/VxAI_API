from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, 
    UserCreateSerializer, 
    UserUpdateSerializer,
    ChangePasswordSerializer,
    PhoneSerializer,
    SMSVerificationSerializer,
    SMSLoginSerializer
)
from .utils.views import SoftDeleteViewSet
from .utils.permissions import IsSelf, IsAdminUserOrReadOnly
from .utils.response import success_response, error_response
from .utils.logger import api_logger
from .utils.sms import SMSUtil

User = get_user_model()

class SMSVerificationView(APIView):
    """
    短信验证码视图
    """
    permission_classes = [AllowAny]
    
    @api_logger
    def post(self, request):
        """
        发送短信验证码
        """
        serializer = PhoneSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            success, message = SMSUtil.send_verification_code(phone)
            if success:
                return success_response(msg=message)
            return error_response(msg=message)
        return error_response(msg=serializer.errors)

class SMSLoginView(APIView):
    """
    短信验证码登录视图
    """
    permission_classes = [AllowAny]
    
    @api_logger
    def post(self, request):
        """
        短信验证码登录
        """
        serializer = SMSLoginSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.validated_data
            user_serializer = UserSerializer(result['user'])
            return success_response(data={
                'user': user_serializer.data,
                'refresh': result['refresh'],
                'access': result['access']
            })
        return error_response(msg=serializer.errors)

class UserViewSet(SoftDeleteViewSet):
    """
    用户视图集，提供用户的增删改查功能
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """
        根据不同的操作返回不同的序列化器
        """
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        return UserSerializer
    
    def get_permissions(self):
        """
        根据不同的操作返回不同的权限
        """
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy', 'hard_delete']:
            permission_classes = [IsSelf]
        elif self.action in ['list', 'deleted']:
            permission_classes = [IsAdminUserOrReadOnly]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        获取当前用户信息
        """
        serializer = self.get_serializer(request.user)
        return success_response(data=serializer.data)
    
    @action(detail=False, methods=['put'])
    def change_password(self, request):
        """
        修改密码
        """
        user = request.user
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # 检查旧密码
            if not user.check_password(serializer.validated_data['old_password']):
                return error_response(msg="旧密码不正确", code=400)
            
            # 设置新密码
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return success_response(msg="密码修改成功")
        
        return error_response(msg=serializer.errors, code=400)
    
    @api_logger
    def create(self, request, *args, **kwargs):
        """
        重写创建方法，添加日志记录
        """
        return super().create(request, *args, **kwargs)
    
    @api_logger
    def update(self, request, *args, **kwargs):
        """
        重写更新方法，添加日志记录
        """
        return super().update(request, *args, **kwargs)
    
    @api_logger
    def destroy(self, request, *args, **kwargs):
        """
        重写删除方法，添加日志记录
        """
        return super().destroy(request, *args, **kwargs) 