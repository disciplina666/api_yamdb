from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Только админ может изменять, остальные — только читать.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and request.user.is_staff
        )
