"""Recalibrar o contrato vale para frente, nunca para trás.

Esta é a garantia que separa a camada do provedor da porcentagem do usuário: a
plataforma pode remanejar assinaturas, trocar de fornecedor e reestimar
capacidade à vontade, e nada disso mexe no que a conta já viu consumido.
"""
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from contas.auditoria import RegistroDeAuditoria
from contas.models import Instituicao, Perfil, TipoInstituicao
from custos.catalogo import contrato_do_fornecedor
from custos.recalibracao import RecalibracaoNegada, recalibrar_assinatura
from ia.models import ChamadaIA
from limites.servico import estado_cota, registrar_uso

pytestmark = pytest.mark.django_db


@pytest.fixture
def provider(db):
    instituicao, _ = Instituicao.objects.get_or_create(
        codigo="VITIS_SOULS",
        defaults={"nome": "Vitis Souls", "tipo": TipoInstituicao.PROVEDORA},
    )
    return get_user_model().objects.create_superuser(
        email="provider-custos@teste.com",
        password="senha-segura-123",
        instituicao=instituicao,
    )


@pytest.fixture
def diretor(db, instituicao):
    return get_user_model().objects.create_user(
        "diretor-custos@teste.com", "senha-segura-123",
        instituicao=instituicao, perfil=Perfil.DIRETOR,
    )


@pytest.fixture
def contrato_rateado(db):
    from custos.models import ContratoProvedor

    return ContratoProvedor.objects.create(
        fornecedor="fornecedor-rateado",
        modalidade="ASSINATURA_RATEIO",
        mensalidade=Decimal("100"),
        contas_atendidas=200,
        chamadas_por_conta_no_mes=300,
    )


def test_recalibrar_muda_o_rateio_das_chamadas_seguintes(provider, contrato_rateado):
    recalibrar_assinatura(
        contrato=contrato_rateado,
        ator=provider,
        contas_atendidas=400,
        motivo="a assinatura passou a atender o dobro de contas",
    )

    assert contrato_do_fornecedor("fornecedor-rateado").custo_por_chamada == (
        Decimal("100") / Decimal("120000")
    )


def test_recalibrar_nao_mexe_no_consumo_ja_debitado(
    provider, aluno, instituicao, contrato_rateado
):
    """O núcleo do requisito: a % que a conta já gastou não volta atrás."""
    registrar_uso(
        usuario=aluno,
        percentual=Decimal("40"),
        fornecedor="claude",
        modelo="claude-sonnet",
        classe_tarefa="TUTORIA",
        referencia=ChamadaIA.objects.create(instituicao=instituicao, usuario=aluno),
    )
    consumido_antes = estado_cota(aluno).consumido_percentual

    recalibrar_assinatura(
        contrato=contrato_rateado,
        ator=provider,
        contas_atendidas=4000,
        chamadas_por_conta_no_mes=900,
        motivo="rebalanceamento agressivo de capacidade",
    )

    assert estado_cota(aluno).consumido_percentual == consumido_antes == Decimal("40")


def test_recalibrar_e_auditado(provider, contrato_rateado):
    recalibrar_assinatura(
        contrato=contrato_rateado,
        ator=provider,
        contas_atendidas=300,
        motivo="migramos metade das contas para o GPT",
    )

    registro = RegistroDeAuditoria.objects.get(acao="recalibrar_contrato_provedor")
    assert "migramos metade das contas" in registro.motivo
    assert registro.ator == provider


def test_contrato_por_token_nao_tem_rateio_a_recalibrar(provider):
    with pytest.raises(RecalibracaoNegada):
        recalibrar_assinatura(
            contrato=contrato_do_fornecedor("openrouter"),
            ator=provider,
            contas_atendidas=10,
            motivo="tentativa indevida",
        )


def test_motivo_e_obrigatorio(provider, contrato_rateado):
    with pytest.raises(RecalibracaoNegada):
        recalibrar_assinatura(
            contrato=contrato_rateado, ator=provider,
            contas_atendidas=10, motivo="   ",
        )


def test_assinatura_relativa_nao_se_recalibra_por_capacidade(provider):
    """Ela se ajusta pelo fator sobre a referência, não por estimativa."""
    with pytest.raises(RecalibracaoNegada):
        recalibrar_assinatura(
            contrato=contrato_do_fornecedor("claude"), ator=provider,
            contas_atendidas=400, motivo="modo errado de ajustar",
        )


def test_diretor_nao_recalibra_contrato_de_provedor(diretor, contrato_rateado):
    """Contrato com fornecedor é da plataforma, não da escola."""
    with pytest.raises(PermissionError):
        recalibrar_assinatura(
            contrato=contrato_rateado, ator=diretor,
            contas_atendidas=10, motivo="fora do meu escopo",
        )
