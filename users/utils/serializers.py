from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

class BaseModelSerializer(serializers.ModelSerializer):
    """
    基础模型序列化器，提供通用功能
    """
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label=_("创建时间"))
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label=_("更新时间"))
    
    class Meta:
        fields = ['id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SoftDeleteModelSerializer(BaseModelSerializer):
    """
    软删除模型序列化器
    """
    is_deleted = serializers.BooleanField(read_only=True, label=_("是否删除"))
    deleted_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, label=_("删除时间"))
    
    class Meta:
        fields = BaseModelSerializer.Meta.fields + ['is_deleted', 'deleted_at']
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ['is_deleted', 'deleted_at']


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    动态字段模型序列化器
    
    支持通过查询参数动态选择要包含的字段
    例如：?fields=id,name,email
    """
    def __init__(self, *args, **kwargs):
        # 从kwargs中弹出fields参数
        fields = kwargs.pop('fields', None)
        
        # 调用父类的初始化方法
        super().__init__(*args, **kwargs)
        
        # 如果没有指定fields，则返回
        if fields is None:
            return
            
        # 如果fields是字符串，则按逗号分割
        if isinstance(fields, str):
            fields = fields.split(',')
            
        # 获取允许的字段
        allowed = set(fields)
        existing = set(self.fields)
        
        # 移除不在allowed中的字段
        for field_name in existing - allowed:
            self.fields.pop(field_name)


class NestedModelSerializer(serializers.ModelSerializer):
    """
    嵌套模型序列化器
    
    支持通过查询参数动态选择要展开的关联字段
    例如：?expand=user,comments
    """
    def __init__(self, *args, **kwargs):
        # 从kwargs中弹出expand参数
        expand = kwargs.pop('expand', None)
        
        # 调用父类的初始化方法
        super().__init__(*args, **kwargs)
        
        # 如果没有指定expand，则返回
        if expand is None:
            return
            
        # 如果expand是字符串，则按逗号分割
        if isinstance(expand, str):
            expand = expand.split(',')
            
        # 获取要展开的字段
        for field_name in expand:
            # 检查字段是否存在
            if field_name not in self.fields:
                continue
                
            # 获取字段
            field = self.fields[field_name]
            
            # 如果字段是PrimaryKeyRelatedField，则替换为嵌套序列化器
            if isinstance(field, serializers.PrimaryKeyRelatedField):
                # 获取关联模型
                model = field.queryset.model
                
                # 创建嵌套序列化器
                class NestedSerializer(serializers.ModelSerializer):
                    class Meta:
                        model = model
                        fields = '__all__'
                
                # 替换字段
                self.fields[field_name] = NestedSerializer(many=field.many, read_only=True)


class RecursiveSerializer(serializers.Serializer):
    """
    递归序列化器，用于序列化树形结构
    """
    def to_representation(self, instance):
        # 获取序列化器类
        serializer = self.parent.parent.__class__(instance, context=self.context)
        return serializer.data 