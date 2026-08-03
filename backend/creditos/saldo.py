from decimal import Decimal

from django.db.models import Sum

from .models import Lancamento, TipoLancamento

_SINAL = {
    TipoLancamento.CREDITO: 1,
    TipoLancamento.ALOCACAO: 1,
    TipoLancamento.ESTORNO: 1,
    TipoLancamento.DEBITO: -1,
}


def _saldo(filtro: dict) -> Decimal:
    total = Decimal("0")
    for tipo, sinal in _SINAL.items():
        soma = (
            Lancamento.objects.filter(tipo=tipo, **filtro).aggregate(s=Sum("quantidade"))["s"]
            or Decimal("0")
        )
        total += sinal * soma
    return total


def saldo_usuario(usuario_id) -> Decimal:
    return _saldo({"usuario_id": usuario_id})


def saldo_turma(turma_id) -> Decimal:
    return _saldo({"turma_id": turma_id})


def saldo_instituicao(instituicao_id) -> Decimal:
    """Saldo do pool da instituicao: lancamentos sem usuario nem turma (nao alocados ainda)."""
    return _saldo({"instituicao_id": instituicao_id, "usuario_id": None, "turma_id": None})
