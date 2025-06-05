from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user
            and request.user.is_authenticated
            and (
                getattr(request.user, 'role', None) == 'admin'
                or request.user.is_superuser
                or request.user.is_staff
            )
        )


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return obj.author == request.user


class IsAdminModeratorAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        return (
            request.user.is_admin
            or request.user.is_moderator
            or obj.author == request.user
        )
