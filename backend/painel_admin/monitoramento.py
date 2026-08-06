"""Leitura de consumo do painel, recortada pelo escopo de quem pergunta.

Separado das views porque é regra de agregação, não de HTTP — e porque é o
lugar onde a fronteira entre "percentual" (produto) e "dólar" (plataforma)
precisa ficar visível numa olhada.
"""
from decimal import Decimal

from django.db.models import Count, Sum

from custos.catalogo import contratos_ativos
from limites.ciclo import ciclo_atual
from limites.normalizacao import cota_da_conta
from limites.servico import estado_cota


def consumo_por_conta(escopo, *, ciclo=None):
    """Uma linha por conta que usou IA na competência, na régua da conta."""
    ciclo = ciclo or ciclo_atual()
    linhas = (
        escopo.consumos()
        .filter(ciclo=ciclo)
        .values("usuario_id", "usuario__email", "usuario__perfil")
        .annotate(chamadas=Count("id"), bruto=Sum("percentual"), custo=Sum("custo_bruto"))
        .order_by("-bruto")
    )
    resultado = []
    for linha in linhas:
        conta = escopo.usuarios().filter(pk=linha["usuario_id"]).first()
        if conta is None:
            continue
        lido = cota_da_conta(estado_cota(conta, ciclo=ciclo))
        resultado.append(
            {
                "usuario_id": linha["usuario_id"],
                "email": linha["usuario__email"],
                "perfil": linha["usuario__perfil"],
                "chamadas": linha["chamadas"],
                "consumido_percentual": lido.consumido_percentual,
                "bloqueado": lido.bloqueado,
                # Só a equipe interna recebe o custo em dólar.
                "custo": linha["custo"] if escopo.ve_custo_real else None,
            }
        )
    return resultado


def consumo_por_fornecedor(escopo, *, ciclo=None):
    """Quanto cada fornecedor atendeu na competência.

    É a visão que responde "trocar de provedor mudou o quê?": chamadas de cada
    lado e, para a equipe interna, o custo que cada um gerou.
    """
    ciclo = ciclo or ciclo_atual()
    linhas = (
        escopo.consumos()
        .filter(ciclo=ciclo)
        .values("fornecedor")
        .annotate(chamadas=Count("id"), custo=Sum("custo_bruto"))
        .order_by("-chamadas")
    )
    return [
        {
            "fornecedor": linha["fornecedor"],
            "chamadas": linha["chamadas"],
            "custo": linha["custo"] if escopo.ve_custo_real else None,
            "custo_medio": (
                (linha["custo"] or Decimal("0")) / linha["chamadas"]
                if escopo.ve_custo_real and linha["chamadas"]
                else None
            ),
        }
        for linha in linhas
    ]


def contratos_para_o_painel(escopo):
    """Contratos de provedor. Só a equipe interna enxerga — é custo da plataforma."""
    if not escopo.ve_custo_real:
        return []
    return [
        {
            "objeto": contrato,
            "custo_por_chamada": contrato.custo_por_chamada,
            "chamadas_estimadas": contrato.chamadas_estimadas_no_mes,
        }
        for contrato in contratos_ativos()
    ]
