from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission. Allows access if the requesting user
    owns the object (obj.user == request.user) or is a staff/admin user.
    Read-only safe methods are blocked too — match history is private.
    """

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return obj.user == request.user