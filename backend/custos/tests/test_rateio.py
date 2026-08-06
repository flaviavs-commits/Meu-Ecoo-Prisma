"""Custo comparável entre fornecedores de modelos de cobrança diferentes."""
from decimal import Decimal

import pytest

from custos.catalogo import contrato_do_fornecedor
from custos.models import ContratoProvedor, TarifaModelo
from custos.rateio import custo_da_chamada

pytestmark = pytest.mark.django_db


def test_o_catalogo_inicial_traz_os_tres_fornecedores():
    fornecedores = set(ContratoProvedor.objects.values_list("fornecedor", flat=True))

    assert {"openrouter", "claude", "gpt"} <= fornecedores


def test_chamada_por_token_usa_o_custo_real_do_provedor():
    custo = custo_da_chamada(
        fornecedor="openrouter",
        modelo="deepseek-v4-flash",
        tokens_entrada=1000,
        tokens_saida=500,
        custo_reportado=Decimal("0.00123456"),
    )

    # O provedor sabe o preco melhor que o nosso catalogo.
    assert custo == Decimal("0.00123456")


def test_chamada_por_token_sem_custo_reportado_cai_na_tarifa_do_catalogo():
    custo = custo_da_chamada(
        fornecedor="openrouter",
        modelo="deepseek-v4-flash",
        tokens_entrada=1000,
        tokens_saida=500,
        custo_reportado=None,
    )

    # 1k entrada x 0,0002 + 0,5k saida x 0,0005
    assert custo == Decimal("0.00045000")


def _chamada_padrao(fornecedor, modelo):
    """Mesma chamada em todo lugar: 1k de entrada e 0,5k de saida."""
    return custo_da_chamada(
        fornecedor=fornecedor,
        modelo=modelo,
        tokens_entrada=1000,
        tokens_saida=500,
        custo_reportado=Decimal("0"),
    )


def test_assinatura_pesa_uma_fracao_da_referencia_e_ignora_o_custo_zero():
    referencia = _chamada_padrao("openrouter", "deepseek-v4-flash")
    claude = _chamada_padrao("claude", "claude-sonnet")

    assert referencia == Decimal("0.00045000")
    # Fator 0,4: a mesma chamada pesa 40% do que pesaria no OpenRouter.
    assert claude == referencia * Decimal("0.4")
    assert claude > 0


def test_o_openrouter_consome_mais_rapido_que_as_assinaturas():
    """Requisito da usuária: por token consome mais rápido que assinatura."""
    referencia = _chamada_padrao("openrouter", "deepseek-v4-flash")

    assert _chamada_padrao("claude", "claude-sonnet") < referencia
    assert _chamada_padrao("gpt", "gpt-luna") < referencia


def test_uma_assinatura_bem_diluida_quase_nao_compromete_o_limite():
    """Claude Max alimentando centenas de alunos: peso por chamada minúsculo."""
    contrato = contrato_do_fornecedor("claude")
    contrato.fator_sobre_referencia = Decimal("0.02")
    contrato.save(update_fields=["fator_sobre_referencia"])

    referencia = _chamada_padrao("openrouter", "deepseek-v4-flash")
    claude = _chamada_padrao("claude", "claude-sonnet")

    assert claude == referencia * Decimal("0.02")


def test_o_peso_da_assinatura_acompanha_o_tamanho_da_chamada():
    """Ancorar na referência faz o fator escalar sozinho com a chamada."""
    pequena = custo_da_chamada(
        fornecedor="claude", modelo="claude-sonnet",
        tokens_entrada=1000, tokens_saida=500, custo_reportado=Decimal("0"),
    )
    grande = custo_da_chamada(
        fornecedor="claude", modelo="claude-sonnet",
        tokens_entrada=2000, tokens_saida=1000, custo_reportado=Decimal("0"),
    )

    assert grande == pequena * 2


def test_a_assinatura_por_rateio_continua_disponivel():
    """O modo antigo segue valendo para contrato que preferir medir assim."""
    contrato = ContratoProvedor.objects.create(
        fornecedor="fornecedor-rateado",
        modalidade="ASSINATURA_RATEIO",
        mensalidade=Decimal("100"),
        contas_atendidas=200,
        chamadas_por_conta_no_mes=300,
    )

    assert contrato.custo_por_chamada == Decimal("100") / Decimal("60000")

    contrato.contas_atendidas = 400
    contrato.save(update_fields=["contas_atendidas"])
    # Mesma mensalidade diluida no dobro do uso: metade do peso por chamada.
    assert contrato_do_fornecedor("fornecedor-rateado").custo_por_chamada == (
        Decimal("100") / Decimal("120000")
    )


def test_fornecedor_fora_do_catalogo_nao_zera_a_contagem():
    """Ligar um provedor novo antes de cadastrá-lo não pode dar uso de graça."""
    custo = custo_da_chamada(
        fornecedor="provedor-novo-ainda-nao-cadastrado",
        modelo="modelo-x",
        tokens_entrada=10,
        tokens_saida=10,
        custo_reportado=Decimal("0.005"),
    )

    assert custo == Decimal("0.005")


def test_contrato_inativo_nao_e_usado():
    ContratoProvedor.objects.filter(fornecedor="claude").update(ativo=False)

    custo = custo_da_chamada(
        fornecedor="claude",
        modelo="claude-sonnet",
        tokens_entrada=10,
        tokens_saida=10,
        custo_reportado=Decimal("0"),
    )

    assert custo == Decimal("0")


def test_assinatura_sem_capacidade_estimada_nao_divide_por_zero():
    contrato = ContratoProvedor.objects.create(
        fornecedor="assinatura-vazia",
        modalidade="ASSINATURA_RATEIO",
        mensalidade=Decimal("50"),
        contas_atendidas=0,
        chamadas_por_conta_no_mes=0,
    )

    assert contrato.custo_por_chamada == Decimal("0")
