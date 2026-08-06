from django.db import IntegrityError, transaction

from contas.auditoria import RegistroDeAuditoria
from contas.models import (
    CODIGO_PROVEDORA,
    PERFIS_INTERNOS,
    TIPOS_INTERNOS,
    Instituicao,
    Perfil,
    TipoInstituicao,
    Usuario,
)


class UsuarioEdicaoNegada(ValueError):
    pass


@transaction.atomic
def editar_usuario(
    *,
    alvo: Usuario,
    ator: Usuario,
    email: str,
    nome: str,
    sobrenome: str,
    instituicao: Instituicao,
    perfil: str,
    ativo: bool,
    motivo: str,
):
    if not ator.eh_staff_interno:
        raise PermissionError("Somente a equipe interna pode editar usuários.")
    # O ADMINISTRADOR administra conta de instituicao-cliente. Sem estas tres
    # guardas ele editaria a si mesmo para PROVIDER e viraria superadmin.
    if not ator.eh_provider:
        if alvo.perfil in PERFIS_INTERNOS:
            raise PermissionError("Conta da equipe só é editada por um provider Vitis Souls.")
        if perfil in PERFIS_INTERNOS:
            raise PermissionError("Somente um provider Vitis Souls concede perfil da equipe.")
        if instituicao.tipo in TIPOS_INTERNOS:
            raise PermissionError("Somente um provider Vitis Souls move conta para a equipe.")
    if alvo.pk == ator.pk:
        raise UsuarioEdicaoNegada("A conta atual não pode ser editada por este fluxo.")
    motivo = str(motivo or "").strip()
    if not motivo:
        raise UsuarioEdicaoNegada("Informe o motivo da edição.")
    if perfil not in Perfil.values:
        raise UsuarioEdicaoNegada("Perfil inválido.")
    if not instituicao.ativa and ativo:
        raise UsuarioEdicaoNegada("Uma conta ativa precisa pertencer a uma instituição ativa.")
    if perfil == Perfil.PROVIDER or alvo.is_superuser:
        if not alvo.is_superuser or perfil != Perfil.PROVIDER:
            raise UsuarioEdicaoNegada("O tier PROVIDER exige superadmin.")
        if (
            instituicao.codigo != CODIGO_PROVEDORA
            or instituicao.tipo != TipoInstituicao.PROVEDORA
            or not ativo
        ):
            raise UsuarioEdicaoNegada("PROVIDER precisa permanecer ativo na Vitis Souls.")
    elif perfil == Perfil.ADMINISTRADOR:
        if instituicao.tipo != TipoInstituicao.PRISMA:
            raise UsuarioEdicaoNegada("O ADMINISTRADOR pertence à instituição interna Prisma.")
    elif instituicao.tipo in TIPOS_INTERNOS:
        raise UsuarioEdicaoNegada("Contas acadêmicas não podem pertencer à equipe interna.")

    email = email.strip().lower()
    nome = nome.strip()
    sobrenome = sobrenome.strip()
    if not email or not nome:
        raise UsuarioEdicaoNegada("E-mail e nome são obrigatórios.")
    # `__iexact`, e nao igualdade exata: `normalize_email` so normaliza o
    # dominio, entao contas antigas podem ter maiuscula na parte local e o
    # indice unico do Postgres diferencia maiuscula de minuscula. Com igualdade
    # exata, editar para `ana@x.com` passava por cima de um `Ana@x.com` ja
    # existente e criava duas contas que a pessoa nao distingue no login.
    # Mesmo criterio de `painel_admin/forms/conta_teste.py`.
    if Usuario.objects.filter(email__iexact=email).exclude(pk=alvo.pk).exists():
        raise UsuarioEdicaoNegada("Já existe uma conta com este e-mail.")

    anterior = f"{alvo.email} / {alvo.perfil} / {alvo.instituicao_id} / {alvo.ativo}"
    alvo.email = email
    alvo.first_name = nome
    alvo.last_name = sobrenome
    alvo.instituicao = instituicao
    alvo.perfil = perfil
    alvo.ativo = ativo
    alvo.is_active = ativo
    try:
        alvo.save(update_fields=[
            "email", "first_name", "last_name", "instituicao", "perfil",
            "ativo", "is_active", "atualizado_em",
        ])
    except IntegrityError as erro:
        raise UsuarioEdicaoNegada("Já existe uma conta com este e-mail.") from erro
    RegistroDeAuditoria.objects.create(
        ator=ator,
        acao="editar_usuario",
        objeto_tipo="Usuario",
        objeto_id=str(alvo.pk),
        motivo=f"{anterior} -> {alvo.email} / {alvo.perfil} / {alvo.instituicao_id} / {alvo.ativo}: {motivo}",
    )
    return alvo
