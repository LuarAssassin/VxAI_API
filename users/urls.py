from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import UserViewSet, SMSVerificationView, SMSLoginView

# 创建路由器
router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    # JWT认证相关
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 短信验证码相关
    path('sms/send/', SMSVerificationView.as_view(), name='sms_send'),
    path('sms/login/', SMSLoginView.as_view(), name='sms_login'),
    
    # 用户相关，使用视图集路由
    path('', include(router.urls)),
] 