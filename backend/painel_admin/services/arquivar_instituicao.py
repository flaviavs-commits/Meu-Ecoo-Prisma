from django.db import transaction

from contas.auditoria import RegistroDeAuditoria
from contas.models import Instituicao, TipoInstituicao, Usuario


class ArquivamentoInstituicaoNegado(ValueError):
    pass


@transaction.atomic
def arquivar_instituicao(*, alvo: Instituicao, ator: Usuario, confirmado: bool, motivo: str):
    if not ator.eh_mantenedor:
        raise PermissionError("Somente um mantenedor Vitis Souls pode arquivar instituições.")
    if alvo.tipo == TipoInstituicao.MANTENEDORA:
        raise ArquivamentoInstituicaoNegado("A instituição Vitis Souls não pode ser arquivada.")
    if not confirmado:
        raise ArquivamentoInstituicaoNegado("Confirme o arquivamento para continuar.")
    motivo = str(motivo or "").strip()
    if not motivo:
        raise ArquivamentoInstituicaoNegado("Informe o motivo do arquivamento.")
    if not alvo.ativa:
        raise ArquivamentoInstituicaoNegado("A instituição já está arquivada.")

    alvo.ativa = False
    alvo.save(update_fields=["ativa", "atualizado_em"])
    Usuario.objects.filter(instituicao=alvo, is_active=True).update(
        ativo=False,
        is_active=False,
    )
    RegistroDeAuditoria.objects.create(
        ator=ator,
        acao="arquivar_instituicao",
        objeto_tipo="Instituicao",
        objeto_id=str(alvo.pk),
        motivo=motivo,
    )
    return alvo
