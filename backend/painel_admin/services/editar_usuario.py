from django.db import IntegrityError, transaction

from contas.auditoria import RegistroDeAuditoria
from contas.models import Instituicao, Perfil, TipoInstituicao, Usuario


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
    if not ator.eh_mantenedor:
        raise PermissionError("Somente um mantenedor Vitis Souls pode editar usuários.")
    if alvo.pk == ator.pk:
        raise UsuarioEdicaoNegada("A conta atual não pode ser editada por este fluxo.")
    motivo = str(motivo or "").strip()
    if not motivo:
        raise UsuarioEdicaoNegada("Informe o motivo da edição.")
    if perfil not in Perfil.values:
        raise UsuarioEdicaoNegada("Perfil inválido.")
    if not instituicao.ativa and ativo:
        raise UsuarioEdicaoNegada("Uma conta ativa precisa pertencer a uma instituição ativa.")
    if perfil == Perfil.MANTENEDOR or alvo.is_superuser:
        if not alvo.is_superuser or perfil != Perfil.MANTENEDOR:
            raise UsuarioEdicaoNegada("O tier MANTENEDOR exige superadmin.")
        if (
            instituicao.codigo != "VITIS_SOULS"
            or instituicao.tipo != TipoInstituicao.MANTENEDORA
            or not ativo
        ):
            raise UsuarioEdicaoNegada("MANTENEDOR precisa permanecer ativo na Vitis Souls.")
    elif instituicao.tipo == TipoInstituicao.MANTENEDORA:
        raise UsuarioEdicaoNegada("Contas acadêmicas não podem pertencer à Vitis Souls.")

    email = email.strip().lower()
    nome = nome.strip()
    sobrenome = sobrenome.strip()
    if not email or not nome:
        raise UsuarioEdicaoNegada("E-mail e nome são obrigatórios.")
    if Usuario.objects.filter(email=email).exclude(pk=alvo.pk).exists():
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
