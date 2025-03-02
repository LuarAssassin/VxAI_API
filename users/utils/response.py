"""
状态码说明:
HTTP状态码:
- 200: 请求成功
- 400: 错误的请求
- 401: 未授权
- 403: 权限不足
- 404: 资源不存在
- 500: 服务器内部错误

业务状态码:
- 0: 成功
- 200: 成功
- 400: 客户端错误
- 401: 未授权
- 403: 权限不足
- 404: 资源不存在
- 500: 服务器错误
"""

from rest_framework.response import Response
from rest_framework import status

class APIResponse(Response):
    """
    自定义API响应类，统一响应格式
    """
    def __init__(self, data=None, code=None, msg=None, status=None, template_name=None, headers=None,
                 exception=False, content_type=None, **kwargs):
        """
        :param data: 响应数据
        :param code: 业务状态码
        :param msg: 响应消息
        :param status: HTTP状态码
        """
        # 默认状态
        std_data = {
            "code": code or 0,
            "message": msg or "success",
        }
        
        # 如果有数据则添加到响应中
        if data is not None:
            std_data["data"] = data
            
        # 添加额外参数
        std_data.update(kwargs)
            
        super().__init__(data=std_data, status=status, template_name=template_name, headers=headers,
                         exception=exception, content_type=content_type)


def success_response(data=None, msg="操作成功", code=200, status_code=status.HTTP_200_OK, **kwargs):
    """
    成功响应
    """
    return APIResponse(data=data, msg=msg, code=code, status=status_code, **kwargs)


def error_response(msg="操作失败", code=400, status_code=status.HTTP_400_BAD_REQUEST, **kwargs):
    """
    错误响应
    """
    return APIResponse(msg=msg, code=code, status=status_code, **kwargs)


def server_error_response(msg="服务器内部错误", code=500, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, **kwargs):
    """
    服务器错误响应
    """
    return APIResponse(msg=msg, code=code, status=status_code, **kwargs)


def not_found_response(msg="资源不存在", code=404, status_code=status.HTTP_404_NOT_FOUND, **kwargs):
    """
    资源不存在响应
    """
    return APIResponse(msg=msg, code=code, status=status_code, **kwargs)


def forbidden_response(msg="权限不足", code=403, status_code=status.HTTP_403_FORBIDDEN, **kwargs):
    """
    权限不足响应
    """
    return APIResponse(msg=msg, code=code, status=status_code, **kwargs)


def unauthorized_response(msg="未授权", code=401, status_code=status.HTTP_401_UNAUTHORIZED, **kwargs):
    """
    未授权响应
    """
    return APIResponse(msg=msg, code=code, status=status_code, **kwargs) 