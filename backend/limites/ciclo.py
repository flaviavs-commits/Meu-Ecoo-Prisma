"""Competencia mensal do limite de uso.

O plano e vendido por conta/mes (E15), entao o percentual consumido precisa
ser contado dentro de uma janela e nao desde o inicio dos tempos. Este modulo
e a unica fonte da regra: quem quiser mudar de mes-calendario para ciclo por
data de assinatura mexe aqui, nao no servico nem nas views.

O ciclo e gravado em `ConsumoIA.ciclo` no momento do debito, em vez de ser
derivado de `criado_em` na leitura. Assim o registro continua append-only e
auditavel: mudar a regra de janela no futuro nao reescreve retroativamente a
competencia de um consumo que ja foi cobrado.
"""

from django.utils import timezone


FORMATO = "%Y-%m"
TAMANHO = 7


def ciclo_de(momento) -> str:
    """Competencia (`YYYY-MM`) a que pertence um instante."""
    return timezone.localtime(momento).strftime(FORMATO)


def ciclo_atual() -> str:
    """Competencia aberta agora."""
    return ciclo_de(timezone.now())
