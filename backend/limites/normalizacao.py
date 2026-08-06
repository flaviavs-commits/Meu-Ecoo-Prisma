"""Converte a cota interna na leitura que a conta enxerga.

A conta **sempre vê 100% como teto**, qualquer que seja o plano da escola. O
que muda entre Prisma, Pro e Ultra é quanto de uso real cabe dentro desses
100% - a *capacidade*, que é assunto da plataforma e não do usuário.

Duas razões para a normalização morar aqui, e não no serviço:

1. O usuário não descobre o tamanho do plano nem o custo por trás dele. A
   plataforma opera vários provedores de IA e a conversão custo -> percentual é
   ajustada conforme a demanda geral do aplicativo; expor a escala entregaria
   uma mecânica que muda debaixo dele e não significa nada para ele.
2. Trocar de plano não muda a escala que a conta lê. Um aluno que estava em 40%
   no Prisma continua em 40% depois do upgrade para Ultra - o que aumentou foi
   o quanto ele consegue fazer dentro daqueles 40%, não o número na tela.

O portão de uso (`autorizar_uso`) continua decidindo sobre o estado interno:
normalizar é uma operação de leitura, nunca de autorização.
"""
from dataclasses import dataclass
from decimal import Decimal

TETO_DA_CONTA = Decimal("100")
CASAS = Decimal("0.0001")


@dataclass(frozen=True)
class CotaDaConta:
    """A cota como a conta a lê: percentual de 0 a 100, sem unidade de custo."""

    ciclo: str
    limite_percentual: Decimal
    consumido_percentual: Decimal
    disponivel_percentual: Decimal
    bloqueado: bool


def cota_da_conta(estado):
    """Reescala o `EstadoCota` interno para a régua de 0 a 100 da conta."""
    capacidade = estado.limite_percentual
    if capacidade <= 0:
        # Plano sem capacidade: não há régua para normalizar, a conta está cheia.
        consumido = TETO_DA_CONTA
    else:
        consumido = (estado.consumido_percentual / capacidade) * TETO_DA_CONTA
    # O estouro de uma chamada é possível por desenho (ver `registrar_uso`), mas
    # a conta não precisa ler "103%": o teto é 100 e o bloqueio já é explícito.
    consumido = min(max(consumido, Decimal("0")), TETO_DA_CONTA).quantize(CASAS)
    return CotaDaConta(
        ciclo=estado.ciclo,
        limite_percentual=TETO_DA_CONTA.quantize(CASAS),
        consumido_percentual=consumido,
        disponivel_percentual=(TETO_DA_CONTA - consumido).quantize(CASAS),
        bloqueado=estado.bloqueado,
    )


def percentual_da_conta(percentual_bruto, capacidade):
    """Reescala o percentual de uma chamada isolada para a mesma régua."""
    if capacidade <= 0:
        return TETO_DA_CONTA.quantize(CASAS)
    return ((percentual_bruto / capacidade) * TETO_DA_CONTA).quantize(CASAS)
