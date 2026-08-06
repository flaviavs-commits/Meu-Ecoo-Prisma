from rest_framework.permissions import BasePermission


class EProvider(BasePermission):
    def has_permission(self, request, view):
        return bool(getattr(request.user, "eh_provider", False))
