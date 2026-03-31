from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Grants access only if the requesting user is the comment author."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
