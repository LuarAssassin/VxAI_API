from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .response import success_response, error_response
from .logger import api_logger

class BaseViewSet(viewsets.GenericViewSet):
    """
    基础视图集，提供通用方法
    """
    
    @api_logger
    def dispatch(self, request, *args, **kwargs):
        """
        重写dispatch方法，添加日志记录
        """
        return super().dispatch(request, *args, **kwargs)
    
    def get_object_by_pk(self, pk):
        """
        通过主键获取对象
        """
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj


class CRUDViewSet(BaseViewSet,
                 mixins.CreateModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 mixins.ListModelMixin):
    """
    完整的CRUD视图集，提供增删改查功能
    """
    
    def create(self, request, *args, **kwargs):
        """
        重写创建方法，使用自定义响应格式
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return success_response(
            data=serializer.data,
            msg="创建成功",
            status_code=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def retrieve(self, request, *args, **kwargs):
        """
        重写检索方法，使用自定义响应格式
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)
    
    def update(self, request, *args, **kwargs):
        """
        重写更新方法，使用自定义响应格式
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        if getattr(instance, '_prefetched_objects_cache', None):
            # 如果使用了预取相关对象，则清除缓存
            instance._prefetched_objects_cache = {}
            
        return success_response(data=serializer.data, msg="更新成功")
    
    def destroy(self, request, *args, **kwargs):
        """
        重写删除方法，使用自定义响应格式
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(msg="删除成功", status_code=status.HTTP_204_NO_CONTENT)
    
    def list(self, request, *args, **kwargs):
        """
        重写列表方法，使用自定义响应格式
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)


class SoftDeleteViewSet(CRUDViewSet):
    """
    软删除视图集，提供软删除和恢复功能
    """
    
    def destroy(self, request, *args, **kwargs):
        """
        重写删除方法，实现软删除
        """
        instance = self.get_object()
        instance.delete()  # 调用模型的软删除方法
        return success_response(msg="删除成功", status_code=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        恢复已删除的对象
        """
        # 使用all_objects管理器获取已删除的对象
        queryset = self.get_queryset().model.all_objects.filter(pk=pk, is_deleted=True)
        instance = get_object_or_404(queryset)
        self.check_object_permissions(request, instance)
        
        # 恢复对象
        instance.restore()
        
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, msg="恢复成功")
    
    @action(detail=True, methods=['delete'])
    def hard_delete(self, request, pk=None):
        """
        硬删除对象
        """
        # 使用all_objects管理器获取对象
        queryset = self.get_queryset().model.all_objects.filter(pk=pk)
        instance = get_object_or_404(queryset)
        self.check_object_permissions(request, instance)
        
        # 硬删除对象
        instance.hard_delete()
        
        return success_response(msg="永久删除成功", status_code=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def deleted(self, request):
        """
        获取已删除的对象列表
        """
        # 使用only_deleted方法获取已删除的对象
        queryset = self.get_queryset().model.objects.only_deleted()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data) 