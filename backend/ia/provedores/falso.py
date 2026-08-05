from decimal import Decimal

from .base import ProvedorIA, ResultadoProvedor
from .roteiros import resposta_para


TEXTO_PADRAO = "Resposta deterministica do provedor falso."


class ProvedorFalso(ProvedorIA):
    """Provedor deterministico para testes e desenvolvimento sem custo externo.

    Quando o prompt declara um contrato de saida estruturada, responde no
    formato pedido - que e o que um provedor real faz. Ver `roteiros.py`.
    """

    def gerar(self, prompt: str, modelo: str, timeout: float = 10) -> ResultadoProvedor:
        return ResultadoProvedor(
            texto=resposta_para(prompt) or TEXTO_PADRAO,
            tokens_entrada=1,
            tokens_saida=1,
            modelo=modelo,
            custo_bruto=Decimal("0.002"),
            fornecedor="falso",
        )
