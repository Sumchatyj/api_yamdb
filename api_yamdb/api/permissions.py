from rest_framework import permissions


class IsAuthorOrStaffOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
            or request.user.is_superuser
        )

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return request.method in permissions.SAFE_METHODS
        return True


class IsAdminOrSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_admin or request.user.is_superuser
        )


class IsAdminOrSuperuserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return request.method in permissions.SAFE_METHODS
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin or request.user.is_superuser
        )
