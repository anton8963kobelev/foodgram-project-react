from rest_framework import permissions


class IsAuthenticatedReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS and
                request.user.is_authenticated)


class IsAuthorOrAdminorReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (obj.author == request.user) or (request.user.is_superuser)
