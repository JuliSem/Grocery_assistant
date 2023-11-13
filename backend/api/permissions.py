from rest_framework import permissions


class ReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

class IsAuthorOrReadOnly(permissions.BasePermission):
    """Permission для класса Recipe."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )
    
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user