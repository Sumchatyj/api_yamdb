from rest_framework import permissions


class IsAuthorOrStaffOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return (request.method in permissions.SAFE_METHODS)
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.role == 'admin'
            or request.user.role == 'moderator'
            or request.user.is_superuser is True
        )


class IsAdminOrSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return (False)
        return (
            request.user.role == 'admin' or request.user.is_superuser is True
        )
