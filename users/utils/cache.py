from django.core.cache import cache
from functools import wraps
import hashlib
import json
import time

def generate_cache_key(prefix, *args, **kwargs):
    """
    生成缓存键
    """
    # 将参数转换为字符串
    args_str = json.dumps(args, sort_keys=True)
    kwargs_str = json.dumps(kwargs, sort_keys=True)
    
    # 使用MD5生成唯一键
    key = f"{prefix}:{args_str}:{kwargs_str}"
    return hashlib.md5(key.encode()).hexdigest()

def cache_result(timeout=300, prefix='cache'):
    """
    缓存装饰器，缓存函数返回结果
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = generate_cache_key(f"{prefix}:{func.__name__}", *args, **kwargs)
            
            # 尝试从缓存获取结果
            result = cache.get(cache_key)
            
            # 如果缓存中没有结果，则执行函数并缓存结果
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)
                
            return result
        return wrapper
    return decorator

def invalidate_cache(prefix, *args, **kwargs):
    """
    使缓存失效
    """
    cache_key = generate_cache_key(prefix, *args, **kwargs)
    cache.delete(cache_key)

def cache_page_result(timeout=300, prefix='page'):
    """
    缓存视图返回结果的装饰器
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            # 对于非GET请求，不使用缓存
            if request.method != 'GET':
                return view_func(self, request, *args, **kwargs)
            
            # 生成缓存键
            path = request.path
            query_string = request.META.get('QUERY_STRING', '')
            user_id = request.user.id if request.user.is_authenticated else 'anonymous'
            cache_key = generate_cache_key(f"{prefix}:{path}", query_string, user_id)
            
            # 尝试从缓存获取结果
            result = cache.get(cache_key)
            
            # 如果缓存中没有结果，则执行视图函数并缓存结果
            if result is None:
                result = view_func(self, request, *args, **kwargs)
                cache.set(cache_key, result, timeout)
                
            return result
        return wrapper
    return decorator

class RateLimiter:
    """
    速率限制器，用于限制API请求频率
    """
    def __init__(self, key_prefix, limit=100, period=60):
        """
        初始化速率限制器
        :param key_prefix: 缓存键前缀
        :param limit: 在period时间内允许的最大请求次数
        :param period: 时间周期，单位为秒
        """
        self.key_prefix = key_prefix
        self.limit = limit
        self.period = period
        
    def is_allowed(self, identifier):
        """
        检查是否允许请求
        :param identifier: 请求标识符，通常是用户ID或IP地址
        :return: 是否允许请求
        """
        cache_key = f"{self.key_prefix}:{identifier}"
        
        # 获取当前计数和过期时间
        count, expire_at = cache.get(cache_key, (0, 0))
        
        # 获取当前时间
        now = time.time()
        
        # 如果已过期，重置计数
        if now > expire_at:
            count = 0
            expire_at = now + self.period
            
        # 增加计数
        count += 1
        
        # 更新缓存
        cache.set(cache_key, (count, expire_at), self.period)
        
        # 检查是否超过限制
        return count <= self.limit
        
    def get_remaining(self, identifier):
        """
        获取剩余的请求次数
        :param identifier: 请求标识符
        :return: 剩余的请求次数
        """
        cache_key = f"{self.key_prefix}:{identifier}"
        
        # 获取当前计数和过期时间
        count, expire_at = cache.get(cache_key, (0, 0))
        
        # 获取当前时间
        now = time.time()
        
        # 如果已过期，重置计数
        if now > expire_at:
            return self.limit
            
        return max(0, self.limit - count) 