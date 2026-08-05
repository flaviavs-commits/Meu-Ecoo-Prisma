from decimal import Decimal

from .base import ProvedorIA, ResultadoProvedor


class ProvedorFalso(ProvedorIA):
    """Provedor deterministico para testes e desenvolvimento sem custo externo."""

    def gerar(self, prompt: str, modelo: str, timeout: float = 10) -> ResultadoProvedor:
        return ResultadoProvedor(
            texto="Resposta deterministica do provedor falso.",
            tokens_entrada=1,
            tokens_saida=1,
            modelo=modelo,
            custo_bruto=Decimal("0.002"),
            fornecedor="falso",
        )
