from functools import wraps

from django.core.exceptions import PermissionDenied

from .escopo import pode_entrar_no_painel


def exige_acesso_ao_painel(view):
    """Portão mais externo: provider, administrador ou diretor de escola.

    Passar por aqui **não** dá acesso a dado de outra escola. Quem entra pelo
    tier de diretor enxerga apenas a própria instituição, e é `escopo.py` que
    faz esse recorte em cada view.
    """
    @wraps(view)
    def protegida(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not pode_entrar_no_painel(request.user):
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return protegida


def _exige(atributo):
    """Monta o decorator de portao a partir da propriedade de tier do usuario."""
    def decorator(view):
        @wraps(view)
        def protegida(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied
            if not getattr(request.user, atributo, False):
                raise PermissionDenied
            return view(request, *args, **kwargs)

        return protegida

    return decorator


# Acesso irrestrito: financeiro, criacao/arquivamento de entidade de dominio e
# auditoria. So o provider Vitis Souls entra.
exige_superadmin = _exige("eh_provider")

# Gestao de usuario e monitoramento das instituicoes-cliente. Admite tambem o
# ADMINISTRADOR da Prisma, que tem alcance cross-tenant sem poder de escrita
# sobre turma, conteudo, credito ou plano.
exige_staff_interno = _exige("eh_staff_interno")
