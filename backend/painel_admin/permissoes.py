from functools import wraps

from django.core.exceptions import PermissionDenied


def exige_superadmin(view):
    """Permite a view apenas a uma conta ativa com superuser explícito."""
    @wraps(view)
    def protegida(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not request.user.is_active or not request.user.is_superuser:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return protegida
