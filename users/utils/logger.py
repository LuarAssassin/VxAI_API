import logging
import json
import traceback
import uuid
from functools import wraps
from django.conf import settings
from django.utils import timezone

# 创建日志记录器
logger = logging.getLogger('django')

# 自定义JSON编码器，处理UUID类型
class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # 将UUID转换为字符串
            return str(obj)
        return super().default(obj)

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
        query_params = {}
        
        # 检查是否是DRF请求对象，它有query_params属性
        if hasattr(request, 'query_params'):
            query_params = dict(request.query_params)
        # 对于普通Django请求，使用GET
        elif hasattr(request, 'GET'):
            query_params = dict(request.GET)
        
        data = None
        
        # 尝试获取请求体数据
        try:
            if method in ['POST', 'PUT', 'PATCH']:
                # 检查是否是DRF请求对象
                if hasattr(request, 'data'):
                    data = request.data
                    # 如果data是QueryDict，转换为dict
                    if hasattr(data, 'dict'):
                        data = data.dict()
                # 对于普通Django请求，使用POST
                elif hasattr(request, 'POST'):
                    data = request.POST
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
            'user_id': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None,
        }
        
        logger.info(f"API Request: {json.dumps(request_log, ensure_ascii=False, cls=UUIDEncoder)}")
        
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
                'user_id': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None,
            }
            
            # 如果是调试模式，记录响应数据
            if settings.DEBUG:
                try:
                    response_log['data'] = response.data
                except Exception:
                    response_log['data'] = "无法解析的响应数据"
            
            logger.info(f"API Response: {json.dumps(response_log, ensure_ascii=False, cls=UUIDEncoder)}")
            
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
                'user_id': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None,
                'exception': str(exc),
                'traceback': traceback.format_exc(),
            }
            
            logger.error(f"API Exception: {json.dumps(error_log, ensure_ascii=False, cls=UUIDEncoder)}")
            
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
        
        logger.info(f"HTTP Request: {json.dumps(log_data, ensure_ascii=False, cls=UUIDEncoder)}")
        
        return response 