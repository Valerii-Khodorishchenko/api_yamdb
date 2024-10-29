"""Users permissions."""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Access only to admin."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )
