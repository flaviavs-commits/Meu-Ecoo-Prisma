from django.db import transaction

from contas.auditoria import RegistroDeAuditoria
from contas.models import (
    CODIGO_PROVEDORA,
    CODIGO_PRISMA,
    TIPOS_INTERNOS,
    Perfil,
    TipoInstituicao,
    Usuario,
)


class PerfilInvalido(ValueError):
    pass


class MotivoObrigatorio(ValueError):
    pass


@transaction.atomic
def alterar_perfil(*, alvo: Usuario, ator: Usuario, perfil: str, motivo: str) -> Usuario:
    if not ator.eh_provider:
        raise PermissionError("Somente um provider Vitis Souls pode alterar perfis.")
    if perfil not in Perfil.values:
        raise PerfilInvalido("Perfil invalido.")
    if alvo.is_superuser and perfil != Perfil.PROVIDER:
        raise PerfilInvalido("Um superadmin precisa permanecer como PROVIDER.")
    if perfil == Perfil.PROVIDER and not (
        alvo.is_superuser
        and alvo.instituicao_id
        and alvo.instituicao.codigo == CODIGO_PROVEDORA
        and alvo.instituicao.tipo == TipoInstituicao.PROVEDORA
    ):
        raise PerfilInvalido("PROVIDER exige superadmin vinculado a uma provedora.")
    if perfil == Perfil.ADMINISTRADOR and not (
        not alvo.is_superuser
        and alvo.instituicao_id
        and alvo.instituicao.codigo == CODIGO_PRISMA
        and alvo.instituicao.tipo == TipoInstituicao.PRISMA
    ):
        raise PerfilInvalido("ADMINISTRADOR exige conta não-superadmin na instituição Prisma.")
    if (
        perfil not in (Perfil.PROVIDER, Perfil.ADMINISTRADOR)
        and alvo.instituicao_id
        and alvo.instituicao.tipo in TIPOS_INTERNOS
    ):
        raise PerfilInvalido("Contas acadêmicas não podem pertencer à equipe interna.")
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
