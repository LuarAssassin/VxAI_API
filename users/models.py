from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

class SoftDeleteManager(models.Manager):
    """
    软删除管理器，默认只返回未删除的对象
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def all_with_deleted(self):
        """
        返回所有对象，包括已删除的
        """
        return super().get_queryset()
    
    def only_deleted(self):
        """
        只返回已删除的对象
        """
        return super().get_queryset().filter(is_deleted=True)

class BaseModel(models.Model):
    """
    基础模型，包含通用字段
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('唯一ID'))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    
    class Meta:
        abstract = True

class SoftDeleteModel(BaseModel):
    """
    软删除模型基类
    """
    is_deleted = models.BooleanField(default=False, verbose_name=_('是否删除'))
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name=_('删除时间'))
    
    # 定义两个管理器
    objects = SoftDeleteManager()  # 默认管理器，只返回未删除的对象
    all_objects = models.Manager()  # 返回所有对象，包括已删除的
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        """
        重写删除方法，实现软删除
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using)
        
    def hard_delete(self, using=None, keep_parents=False):
        """
        硬删除方法，真正从数据库中删除对象
        """
        return super().delete(using=using, keep_parents=keep_parents)
    
    def restore(self):
        """
        恢复已删除的对象
        """
        self.is_deleted = False
        self.deleted_at = None
        self.save()

class TimeStampedModel(models.Model):
    """
    时间戳模型，包含创建和更新时间
    """
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    
    class Meta:
        abstract = True

class CustomUserManager(BaseUserManager):
    """
    自定义用户管理器，使用邮箱作为唯一标识符
    """
    def create_user(self, phone, username, password=None, **extra_fields):
        """
        创建并保存一个用户
        """
        if not phone:
            raise ValueError(_('必须提供手机号码'))
        
        user = self.model(
            phone=phone,
            username=username,
            **extra_fields
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone, username, password=None, **extra_fields):
        """
        创建并保存一个超级用户
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('超级用户必须设置is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('超级用户必须设置is_superuser=True'))
            
        return self.create_user(phone, username, password, **extra_fields)

class CustomUser(AbstractUser, SoftDeleteModel):
    """
    自定义用户模型，使用邮箱作为唯一标识符，并继承软删除模型
    """
    username = models.CharField(_('用户名'), max_length=150, unique=True)
    email = models.EmailField(_('邮箱地址'), unique=True, blank=True, null=True)
    phone = models.CharField(_('手机号码'), max_length=15, unique=True, default='00000000000')
    is_active = models.BooleanField(_('激活状态'), default=True)
    is_staff = models.BooleanField(_('员工状态'), default=False)
    
    # 自定义字段
    bio = models.TextField(_('个人简介'), blank=True, null=True)
    avatar = models.ImageField(_('头像'), upload_to='avatars/', blank=True, null=True)
    
    # 使用自定义管理器
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        
    def __str__(self):
        return self.phone
        
    def save(self, *args, **kwargs):
        """
        重写保存方法，确保UUID格式正确
        """
        # 如果是新创建的用户且ID不是UUID格式，则生成新的UUID
        if not self.pk or not isinstance(self.pk, uuid.UUID):
            try:
                # 尝试将现有ID转换为UUID
                if self.pk:
                    self.pk = uuid.UUID(str(self.pk))
            except (ValueError, AttributeError):
                # 如果转换失败，生成新的UUID
                self.pk = uuid.uuid4()
        super().save(*args, **kwargs)
