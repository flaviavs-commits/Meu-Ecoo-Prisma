from rest_framework.permissions import BasePermission


class EDonoDoObjeto(BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, "usuario_id", None) == request.user.id
