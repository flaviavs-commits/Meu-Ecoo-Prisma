from rest_framework.permissions import BasePermission

from .e_dono_do_objeto import EDonoDoObjeto


class MesmaInstituicao(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.instituicao_id == request.user.instituicao_id


# Compatibilidade para consumidores da primeira versao da E04.
EDonodoObjeto = EDonoDoObjeto
