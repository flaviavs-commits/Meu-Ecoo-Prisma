from decimal import Decimal

from django.db import transaction

from academico.models import Turma
from contas.auditoria import RegistroDeAuditoria

from .excecoes import AlocacaoForaDaInstituicaoError, AlocacaoSemConfirmacaoError
from .models import Lancamento, TipoLancamento


def alocar(*, instituicao, destino_usuario=None, destino_turma_id=None, quantidade: Decimal, motivo: str, criado_por):
    """Move do pool da instituicao para um perfil/turma: dois lancamentos, uma transacao.

    Nunca um lado sem o outro - se qualquer um falhar, os dois desfazem.
    """
    if destino_usuario and destino_usuario.instituicao_id != instituicao.id:
        raise AlocacaoForaDaInstituicaoError()
    if destino_turma_id is not None and not Turma.objects.filter(
        pk=destino_turma_id, instituicao_id=instituicao.id
    ).exists():
        raise AlocacaoForaDaInstituicaoError()
    if destino_usuario is None and destino_turma_id is None:
        raise ValueError("Alocacao exige usuario ou turma de destino.")

    with transaction.atomic():
        saida = Lancamento.objects.create(
            instituicao=instituicao,
            usuario=None,
            turma_id=None,
            tipo=TipoLancamento.DEBITO,
            quantidade=quantidade,
            motivo=f"Alocacao (saida do pool): {motivo}",
            criado_por=criado_por,
        )
        entrada = Lancamento.objects.create(
            instituicao=instituicao,
            usuario=destino_usuario,
            turma_id=destino_turma_id,
            tipo=TipoLancamento.ALOCACAO,
            quantidade=quantidade,
            motivo=motivo,
            criado_por=criado_por,
        )
    return saida, entrada


def reduzir_alocacao(*, instituicao, origem_usuario=None, origem_turma_id=None, quantidade: Decimal, motivo: str, criado_por, confirmado: bool):
    """Reducao de alocacao ja concedida e acao destrutiva: exige confirmacao + motivo (E04)."""
    if not confirmado or not motivo:
        raise AlocacaoSemConfirmacaoError(
            "Reducao de alocacao exige confirmacao explicita e motivo."
        )
    with transaction.atomic():
        saida = Lancamento.objects.create(
            instituicao=instituicao,
            usuario=origem_usuario,
            turma_id=origem_turma_id,
            tipo=TipoLancamento.DEBITO,
            quantidade=quantidade,
            motivo=f"Reducao de alocacao: {motivo}",
            criado_por=criado_por,
        )
        volta = Lancamento.objects.create(
            instituicao=instituicao,
            usuario=None,
            turma_id=None,
            tipo=TipoLancamento.CREDITO,
            quantidade=quantidade,
            motivo=f"Retorno ao pool: {motivo}",
            criado_por=criado_por,
        )
        objeto_tipo = "Usuario" if origem_usuario else "Turma" if origem_turma_id else "Instituicao"
        objeto_id = origem_usuario.pk if origem_usuario else origem_turma_id or instituicao.pk
        RegistroDeAuditoria.objects.create(
            ator=criado_por,
            acao="reduzir_alocacao",
            objeto_tipo=objeto_tipo,
            objeto_id=str(objeto_id),
            motivo=motivo,
        )
    return saida, volta
