import logging
import json
import traceback
from functools import wraps
from django.conf import settings
from django.utils import timezone

# 创建日志记录器
logger = logging.getLogger('django')

def log_exception(exc):
    """
    记录异常日志
    """
    logger.error(f"Exception: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")

def api_logger(func):
    """
    API日志装饰器，记录API请求和响应
    """
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        # 记录请求开始时间
        start_time = timezone.now()
        
        # 获取请求信息
        method = request.method
        path = request.path
        query_params = dict(request.query_params)
        data = None
        
        # 尝试获取请求体数据
        try:
            if method in ['POST', 'PUT', 'PATCH']:
                data = request.data
                # 如果data是QueryDict，转换为dict
                if hasattr(data, 'dict'):
                    data = data.dict()
        except Exception:
            data = "无法解析的请求数据"
        
        # 记录请求日志
        request_log = {
            'timestamp': start_time.isoformat(),
            'method': method,
            'path': path,
            'query_params': query_params,
            'data': data,
            'user_id': request.user.id if request.user.is_authenticated else None,
        }
        
        logger.info(f"API Request: {json.dumps(request_log, ensure_ascii=False)}")
        
        # 执行视图函数
        try:
            response = func(self, request, *args, **kwargs)
            
            # 计算执行时间
            end_time = timezone.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # 记录响应日志
            response_log = {
                'timestamp': end_time.isoformat(),
                'method': method,
                'path': path,
                'status_code': response.status_code,
                'execution_time': execution_time,
                'user_id': request.user.id if request.user.is_authenticated else None,
            }
            
            # 如果是调试模式，记录响应数据
            if settings.DEBUG:
                try:
                    response_log['data'] = response.data
                except Exception:
                    response_log['data'] = "无法解析的响应数据"
            
            logger.info(f"API Response: {json.dumps(response_log, ensure_ascii=False)}")
            
            return response
            
        except Exception as exc:
            # 记录异常日志
            end_time = timezone.now()
            execution_time = (end_time - start_time).total_seconds()
            
            error_log = {
                'timestamp': end_time.isoformat(),
                'method': method,
                'path': path,
                'execution_time': execution_time,
                'user_id': request.user.id if request.user.is_authenticated else None,
                'exception': str(exc),
                'traceback': traceback.format_exc(),
            }
            
            logger.error(f"API Exception: {json.dumps(error_log, ensure_ascii=False)}")
            
            # 重新抛出异常
            raise
    
    return wrapper


class RequestLogMiddleware:
    """
    请求日志中间件，记录所有HTTP请求
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # 记录请求开始时间
        start_time = timezone.now()
        
        # 获取请求信息
        method = request.method
        path = request.path
        
        # 执行请求
        response = self.get_response(request)
        
        # 计算执行时间
        end_time = timezone.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # 记录请求日志
        log_data = {
            'timestamp': end_time.isoformat(),
            'method': method,
            'path': path,
            'status_code': response.status_code,
            'execution_time': execution_time,
            'user_id': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None,
        }
        
        logger.info(f"HTTP Request: {json.dumps(log_data, ensure_ascii=False)}")
        
        return response 