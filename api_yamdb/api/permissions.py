from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission


# class IsAdminOrReadOnly(permissions.BasePermission):
#     """
#     Только админ может изменять, остальные — только читать.
#     """

#     def has_permission(self, request, view):
#         return (
#             request.method in permissions.SAFE_METHODS
#             or request.user.is_authenticated and request.user.is_staff
#         )

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
