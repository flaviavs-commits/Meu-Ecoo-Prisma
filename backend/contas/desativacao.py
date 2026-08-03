from django.db import transaction

from .auditoria import RegistroDeAuditoria


class DesativacaoNegada(ValueError):
    pass


def desativar_usuario(*, alvo, ator, confirmacao, motivo):
    if confirmacao is not True:
        raise DesativacaoNegada("Confirme a acao para continuar.")
    motivo = str(motivo or "").strip()
    if not motivo:
        raise DesativacaoNegada("Informe o motivo da acao.")
    if not ator.is_staff and (
        ator.perfil != "DIRETOR" or ator.instituicao_id != alvo.instituicao_id
    ):
        raise DesativacaoNegada("Usuario sem permissao para desativar este usuario.")
    if alvo.pk == ator.pk:
        raise DesativacaoNegada("O usuario atual nao pode desativar a propria conta.")

    with transaction.atomic():
        alvo.ativo = False
        alvo.is_active = False
        alvo.save(update_fields=["ativo", "is_active", "atualizado_em"])
        RegistroDeAuditoria.objects.create(
            ator=ator,
            acao="desativar_usuario",
            objeto_tipo="Usuario",
            objeto_id=str(alvo.pk),
            motivo=motivo,
        )
