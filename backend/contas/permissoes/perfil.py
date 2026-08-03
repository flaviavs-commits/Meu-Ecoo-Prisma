from rest_framework.permissions import BasePermission


class PerfilPermission(BasePermission):
    perfil = None

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.perfil == self.perfil)
