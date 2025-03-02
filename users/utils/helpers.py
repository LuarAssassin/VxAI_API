import re
import uuid
import random
import string
import hashlib
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def generate_random_string(length=10):
    """
    生成随机字符串
    """
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def generate_uuid():
    """
    生成UUID
    """
    return str(uuid.uuid4())

def generate_verification_code(length=6):
    """
    生成数字验证码
    """
    return ''.join(random.choice(string.digits) for _ in range(length))

def hash_string(text, salt=None):
    """
    哈希字符串
    """
    if salt is None:
        salt = settings.SECRET_KEY
    
    return hashlib.sha256((text + salt).encode()).hexdigest()

def is_valid_email(email):
    """
    验证邮箱格式
    """
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))

def is_valid_phone(phone):
    """
    验证手机号格式（中国大陆手机号）
    """
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))

def send_verification_email(user, subject, template_name, context=None):
    """
    发送验证邮件
    """
    if context is None:
        context = {}
    
    # 添加用户信息到上下文
    context['user'] = user
    
    # 渲染HTML内容
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)
    
    # 发送邮件
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )

def get_client_ip(request):
    """
    获取客户端IP地址
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def format_datetime(dt, format_str='%Y-%m-%d %H:%M:%S'):
    """
    格式化日期时间
    """
    if dt is None:
        return None
    
    if isinstance(dt, str):
        try:
            dt = datetime.strptime(dt, format_str)
        except ValueError:
            return None
    
    return dt.strftime(format_str)

def get_time_ago(dt):
    """
    获取多久以前的友好显示
    """
    if dt is None:
        return ''
    
    now = timezone.now()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years}年前"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months}个月前"
    elif diff.days > 0:
        return f"{diff.days}天前"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours}小时前"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes}分钟前"
    else:
        return "刚刚"

def truncate_string(text, max_length=100, suffix='...'):
    """
    截断字符串
    """
    if text is None:
        return ''
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + suffix

def safe_int(value, default=0):
    """
    安全地转换为整数
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    """
    安全地转换为浮点数
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_bool(value, default=False):
    """
    安全地转换为布尔值
    """
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        value = value.lower()
        if value in ('true', 'yes', '1', 'y', 't'):
            return True
        elif value in ('false', 'no', '0', 'n', 'f'):
            return False
    
    return default 