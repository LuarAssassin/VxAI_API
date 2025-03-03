"""
短信工具类，用于发送短信验证码
"""
import random
import logging
from django.conf import settings
from django.core.cache import cache
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20210111 import sms_client, models

logger = logging.getLogger('django')

class SMSUtil:
    """
    短信工具类
    """
    @staticmethod
    def generate_code(length=6):
        """
        生成指定长度的随机验证码
        :param length: 验证码长度，默认6位
        :return: 随机验证码
        """
        return ''.join(random.choice('0123456789') for _ in range(length))
    
    @staticmethod
    def send_verification_code(phone):
        """
        发送验证码
        :param phone: 手机号
        :return: (bool, str) - (是否成功, 消息)
        """
        # 生成验证码
        code = SMSUtil.generate_code()
        
        try:
            # 实例化一个认证对象
            cred = credential.Credential(
                settings.TENCENT_CLOUD_SMS['SECRET_ID'], 
                settings.TENCENT_CLOUD_SMS['SECRET_KEY']
            )
            
            # 实例化要请求产品的client对象
            client = sms_client.SmsClient(cred, "ap-guangzhou")
            
            # 实例化一个请求对象
            req = models.SendSmsRequest()
            
            # 设置参数
            req.SmsSdkAppId = settings.TENCENT_CLOUD_SMS['APP_ID']
            req.SignName = settings.TENCENT_CLOUD_SMS['SIGN_NAME']
            req.TemplateId = settings.TENCENT_CLOUD_SMS['TEMPLATE_ID']
            req.TemplateParamSet = [code]
            req.PhoneNumberSet = [f"+86{phone}"]
            
            # 发送短信
            resp = client.SendSms(req)
            
            # 检查发送结果
            if resp.SendStatusSet[0].Code == "Ok":
                # 将验证码存入缓存，设置过期时间
                cache_key = f"{settings.SMS_CODE_CACHE_PREFIX}{phone}"
                cache.set(cache_key, code, settings.SMS_CODE_EXPIRE_MINUTES * 60)
                logger.info(f"短信验证码发送成功: {phone}, 验证码: {code}")
                return True, "验证码发送成功"
            else:
                logger.error(f"短信验证码发送失败: {phone}, 错误: {resp.SendStatusSet[0].Message}")
                return False, f"验证码发送失败: {resp.SendStatusSet[0].Message}"
                
        except TencentCloudSDKException as err:
            logger.error(f"腾讯云SDK异常: {err}")
            return False, f"验证码发送失败: {err}"
        except Exception as e:
            logger.error(f"发送短信验证码异常: {e}")
            return False, "验证码发送失败，请稍后重试"
    
    @staticmethod
    def verify_code(phone, code):
        """
        验证短信验证码
        :param phone: 手机号
        :param code: 验证码
        :return: bool - 验证是否成功
        """
        cache_key = f"{settings.SMS_CODE_CACHE_PREFIX}{phone}"
        cached_code = cache.get(cache_key)
        
        if not cached_code:
            return False
        
        # 验证成功后删除缓存中的验证码
        if cached_code == code:
            cache.delete(cache_key)
            return True
        
        return False 