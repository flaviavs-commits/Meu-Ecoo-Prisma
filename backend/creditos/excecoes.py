class SaldoInsuficienteError(Exception):
    """Levantada quando o saldo do escopo e <= 0. Codigo de API: 'saldo_insuficiente'."""

    codigo = "saldo_insuficiente"


class AlocacaoForaDaInstituicaoError(Exception):
    """Levantada quando uma alocacao tenta atravessar o tenant."""


class AlocacaoSemConfirmacaoError(Exception):
    """Reducao de alocacao exige confirmacao explicita e motivo (mixin destrutivo de E04)."""
