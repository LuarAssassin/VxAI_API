from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.translation import gettext_lazy as _

def custom_exception_handler(exc, context):
    """
    自定义异常处理函数
    """
    # 首先调用REST framework默认的异常处理
    response = exception_handler(exc, context)
    
    # 如果异常没有被REST framework处理，则返回None
    if response is None:
        return None
    
    # 自定义响应格式
    if hasattr(exc, 'detail'):
        error_message = str(exc.detail)
    else:
        error_message = str(exc)
    
    # 获取状态码
    status_code = response.status_code
    
    # 构建自定义响应
    custom_response_data = {
        'code': status_code,
        'message': error_message,
        'success': False,
    }
    
    response.data = custom_response_data
    
    return response


class BusinessException(APIException):
    """
    业务异常基类
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('业务处理异常')
    default_code = 'business_exception'


class ResourceNotFoundException(BusinessException):
    """
    资源不存在异常
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('请求的资源不存在')
    default_code = 'resource_not_found'


class PermissionDeniedException(BusinessException):
    """
    权限不足异常
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _('权限不足，无法执行此操作')
    default_code = 'permission_denied'


class ValidationException(BusinessException):
    """
    数据验证异常
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('数据验证失败')
    default_code = 'validation_error'


class AuthenticationException(BusinessException):
    """
    认证异常
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('认证失败')
    default_code = 'authentication_failed' 