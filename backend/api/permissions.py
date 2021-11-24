from rest_framework import permissions


class IsAuthenticatedReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS and
                request.user.is_authenticated)
