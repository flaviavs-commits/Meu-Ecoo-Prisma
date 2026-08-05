from rest_framework.permissions import BasePermission


class EMantenedor(BasePermission):
    def has_permission(self, request, view):
        return bool(getattr(request.user, "eh_mantenedor", False))
