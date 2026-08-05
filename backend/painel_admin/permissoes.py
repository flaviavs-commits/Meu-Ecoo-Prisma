from functools import wraps

from django.core.exceptions import PermissionDenied


def exige_superadmin(view):
    """Permite a view apenas a um mantenedor Vitis Souls ativo."""
    @wraps(view)
    def protegida(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not request.user.eh_mantenedor:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return protegida
