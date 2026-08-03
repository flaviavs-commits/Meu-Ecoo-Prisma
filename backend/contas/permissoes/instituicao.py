from rest_framework.permissions import BasePermission


class MesmaInstituicao(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.instituicao_id == request.user.instituicao_id


class EDonodoObjeto(BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, "usuario_id", None) == request.user.id
