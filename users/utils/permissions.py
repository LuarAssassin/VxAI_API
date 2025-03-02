from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    自定义权限类，只允许对象的所有者编辑它
    """
    def has_object_permission(self, request, view, obj):
        # 读取权限允许任何请求
        # 所以我们总是允许GET, HEAD 或 OPTIONS 请求
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # 写入权限只允许对象的所有者
        # 假设对象有一个名为`owner`的属性
        return obj.owner == request.user


class IsOwner(permissions.BasePermission):
    """
    自定义权限类，只允许对象的所有者访问
    """
    def has_object_permission(self, request, view, obj):
        # 只允许对象的所有者访问
        # 这里假设对象有一个名为`owner`的属性
        return obj.owner == request.user


class IsSelf(permissions.BasePermission):
    """
    自定义权限类，只允许用户访问自己的信息
    """
    def has_object_permission(self, request, view, obj):
        # 只允许用户访问自己的信息
        return obj.id == request.user.id


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    自定义权限类，只允许管理员用户编辑，其他用户只读
    """
    def has_permission(self, request, view):
        # 读取权限允许任何请求
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # 写入权限只允许管理员
        return request.user and request.user.is_staff 