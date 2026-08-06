"""Consulta ao catálogo de contratos e tarifas.

Isolado do cálculo para que o rateio não converse com o banco direto e para
que trocar a origem do catálogo (banco hoje, cache ou config amanhã) não toque
na regra de custo.
"""
from .models import ContratoProvedor, TarifaModelo


def contrato_do_fornecedor(fornecedor):
    if not fornecedor:
        return None
    return ContratoProvedor.objects.filter(fornecedor=fornecedor, ativo=True).first()


def tarifa_do_modelo(modelo):
    if not modelo:
        return None
    return (
        TarifaModelo.objects.select_related("contrato")
        .filter(modelo=modelo, ativo=True)
        .first()
    )


def tarifa_de_referencia():
    """A régua das assinaturas relativas: a tarifa por token marcada como tal."""
    return TarifaModelo.objects.filter(referencia=True, ativo=True).first()


def contratos_ativos():
    return ContratoProvedor.objects.filter(ativo=True).prefetch_related("tarifas")
