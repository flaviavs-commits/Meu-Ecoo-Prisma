from django.db import transaction

from contas.auditoria import RegistroDeAuditoria
from contas.models import Perfil, Usuario


class PerfilInvalido(ValueError):
    pass


class MotivoObrigatorio(ValueError):
    pass


@transaction.atomic
def alterar_perfil(*, alvo: Usuario, ator: Usuario, perfil: str, motivo: str) -> Usuario:
    if perfil not in Perfil.values:
        raise PerfilInvalido("Perfil invalido.")
    motivo_limpo = motivo.strip()
    if not motivo_limpo:
        raise MotivoObrigatorio("Informe o motivo da troca de perfil.")

    perfil_anterior = alvo.perfil or "SEM_PERFIL"
    alvo.perfil = perfil
    alvo.save(update_fields=("perfil", "atualizado_em"))
    RegistroDeAuditoria.objects.create(
        ator=ator,
        acao="alterar_perfil",
        objeto_tipo="Usuario",
        objeto_id=str(alvo.pk),
        motivo=f"{perfil_anterior} -> {perfil}: {motivo_limpo}",
    )
    return alvo
