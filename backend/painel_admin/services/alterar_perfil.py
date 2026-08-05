from django.db import transaction

from contas.auditoria import RegistroDeAuditoria
from contas.models import Perfil, TipoInstituicao, Usuario


class PerfilInvalido(ValueError):
    pass


class MotivoObrigatorio(ValueError):
    pass


@transaction.atomic
def alterar_perfil(*, alvo: Usuario, ator: Usuario, perfil: str, motivo: str) -> Usuario:
    if not ator.eh_mantenedor:
        raise PermissionError("Somente um mantenedor Vitis Souls pode alterar perfis.")
    if perfil not in Perfil.values:
        raise PerfilInvalido("Perfil invalido.")
    if alvo.is_superuser and perfil != Perfil.MANTENEDOR:
        raise PerfilInvalido("Um superadmin precisa permanecer como MANTENEDOR.")
    if perfil == Perfil.MANTENEDOR and not (
        alvo.is_superuser
        and alvo.instituicao_id
        and alvo.instituicao.codigo == "VITIS_SOULS"
        and alvo.instituicao.tipo == TipoInstituicao.MANTENEDORA
    ):
        raise PerfilInvalido("MANTENEDOR exige superadmin vinculado a uma mantenedora.")
    if perfil != Perfil.MANTENEDOR and alvo.instituicao_id and alvo.instituicao.tipo == TipoInstituicao.MANTENEDORA:
        raise PerfilInvalido("Contas acadêmicas não podem pertencer à Vitis Souls.")
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
