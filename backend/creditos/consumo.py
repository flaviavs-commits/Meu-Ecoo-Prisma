from contextlib import contextmanager
from decimal import Decimal

from django.db import IntegrityError, transaction

from .excecoes import SaldoInsuficienteError
from .models import Lancamento, TipoLancamento, TravaSaldoUsuario
from .saldo import saldo_usuario


@contextmanager
def trava_saldo(usuario):
    """Serializa autorizacao + debito do mesmo usuario. Uso: `with trava_saldo(usuario):`."""
    with transaction.atomic():
        TravaSaldoUsuario.objects.get_or_create(usuario=usuario)
        TravaSaldoUsuario.objects.select_for_update().get(usuario=usuario)
        yield


def autorizar_consumo(usuario) -> Decimal:
    """Gate da regra 'termina e depois bloqueia': autoriza se saldo > 0, mesmo custo maior.

    Deve ser chamada dentro de `trava_saldo(usuario)` para valer contra concorrencia real.
    """
    saldo = saldo_usuario(usuario.id)
    if saldo <= 0:
        raise SaldoInsuficienteError()
    return saldo


def registrar_consumo(*, instituicao, usuario, quantidade: Decimal, motivo: str, referencia, criado_por=None):
    """Debita o custo real apos chamada bem-sucedida. Chamada que falhou nunca chega aqui.

    Idempotente: mesma `referencia` nao debita duas vezes (UniqueConstraint em
    `(referencia, tipo=DEBITO)`). Retry silenciosamente vira no-op.
    """
    try:
        with transaction.atomic():
            return Lancamento.objects.create(
                instituicao=instituicao,
                usuario=usuario,
                tipo=TipoLancamento.DEBITO,
                quantidade=quantidade,
                motivo=motivo,
                referencia=referencia,
                criado_por=criado_por,
            )
    except IntegrityError:
        return Lancamento.objects.get(referencia=referencia, tipo=TipoLancamento.DEBITO)
