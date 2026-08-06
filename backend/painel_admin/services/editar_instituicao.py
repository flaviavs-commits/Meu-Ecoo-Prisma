from django.db import IntegrityError, transaction

from contas.auditoria import RegistroDeAuditoria
from contas.models import TIPOS_INTERNOS, Instituicao, TipoInstituicao, Usuario


class InstituicaoEdicaoNegada(ValueError):
    pass


@transaction.atomic
def editar_instituicao(*, alvo: Instituicao, ator: Usuario, nome: str, documento: str, motivo: str):
    if not ator.eh_provider:
        raise PermissionError("Somente um provider Vitis Souls pode editar instituições.")
    if alvo.tipo in TIPOS_INTERNOS:
        raise InstituicaoEdicaoNegada("Instituição interna da equipe não é alterada por este fluxo.")
    nome = nome.strip()
    documento = documento.strip()
    motivo = str(motivo or "").strip()
    if not nome or not documento or not motivo:
        raise InstituicaoEdicaoNegada("Nome, documento e motivo são obrigatórios.")
    if Instituicao.objects.filter(documento=documento).exclude(pk=alvo.pk).exists():
        raise InstituicaoEdicaoNegada("Já existe uma instituição com este documento.")
    anterior = f"{alvo.nome} / {alvo.documento}"
    try:
        alvo.nome = nome
        alvo.documento = documento
        alvo.save(update_fields=["nome", "documento", "atualizado_em"])
    except IntegrityError as erro:
        raise InstituicaoEdicaoNegada("Já existe uma instituição com este documento.") from erro
    RegistroDeAuditoria.objects.create(
        ator=ator,
        acao="editar_instituicao",
        objeto_tipo="Instituicao",
        objeto_id=str(alvo.pk),
        motivo=f"{anterior} -> {nome} / {documento}: {motivo}",
    )
    return alvo
