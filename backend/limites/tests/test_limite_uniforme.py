"""O limite é uniforme por plano, e a conta sempre lê 100%.

Não existe cota nominal: nenhum perfil aumenta ou diminui o limite de uma conta
isolada. Internamente o plano tem capacidades diferentes (Prisma 100, Pro 171,
Ultra 271 — número comercial, público na landing), mas a conta enxerga sempre
a régua de 0 a 100%. O que aquele 100% comporta de uso real é assunto da
plataforma, que opera vários provedores e ajusta a conversão custo→percentual
conforme a demanda geral do aplicativo.
"""
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from contas.models import Perfil
from ia.models import ChamadaIA
from limites.models import AssinaturaInstituicao, PlanoInstitucional
from limites.normalizacao import cota_da_conta
from limites.servico import estado_cota, registrar_uso

pytestmark = pytest.mark.django_db


def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


def _conta(instituicao, email, perfil):
    return get_user_model().objects.create_user(
        email=email, password="senha-segura-123", instituicao=instituicao, perfil=perfil
    )


def test_todas_as_contas_da_escola_tem_a_mesma_capacidade(aluno, instituicao):
    plano = PlanoInstitucional.objects.get(codigo="PRISMA_PRO")
    AssinaturaInstituicao.objects.create(instituicao=instituicao, plano=plano)
    professor = _conta(instituicao, "prof-uniforme@teste.com", Perfil.PROFESSOR)
    diretor = _conta(instituicao, "dir-uniforme@teste.com", Perfil.DIRETOR)

    capacidades = {
        estado_cota(conta).limite_percentual for conta in (aluno, professor, diretor)
    }

    assert capacidades == {Decimal("171")}


def test_a_capacidade_muda_para_todos_ao_trocar_o_plano_da_escola(aluno, instituicao):
    professor = _conta(instituicao, "prof-plano@teste.com", Perfil.PROFESSOR)
    plano = PlanoInstitucional.objects.get(codigo="PRISMA_ULTRA")
    AssinaturaInstituicao.objects.create(instituicao=instituicao, plano=plano)

    assert estado_cota(aluno).limite_percentual == Decimal("271")
    assert estado_cota(professor).limite_percentual == Decimal("271")


def test_o_consumo_de_uma_conta_nao_mexe_no_limite_da_outra(aluno, instituicao):
    colega = _conta(instituicao, "colega-uniforme@teste.com", Perfil.ALUNO)
    registrar_uso(
        usuario=aluno,
        percentual=Decimal("30"),
        fornecedor="provedor-a",
        modelo="modelo-a",
        classe_tarefa="TUTORIA",
        referencia=ChamadaIA.objects.create(instituicao=instituicao, usuario=aluno),
    )

    assert estado_cota(aluno).consumido_percentual == Decimal("30")
    assert estado_cota(colega).consumido_percentual == Decimal("0")
    assert estado_cota(colega).limite_percentual == estado_cota(aluno).limite_percentual


def test_a_conta_nao_enxerga_custo_nem_provedor_no_proprio_historico(aluno, instituicao):
    registrar_uso(
        usuario=aluno,
        percentual=Decimal("5"),
        fornecedor="provedor-secreto",
        modelo="modelo-secreto",
        classe_tarefa="RESUMO",
        custo_bruto=Decimal("0.01234567"),
        referencia=ChamadaIA.objects.create(instituicao=instituicao, usuario=aluno),
    )

    resposta = cliente(aluno).get("/api/v1/limites/uso/historico/")

    assert resposta.status_code == 200
    registro = resposta.json()["results"][0]
    assert registro["percentual"] == "5.0000"
    # A conta sabe quanto do plano gastou, nao o que isso custou nem quem atendeu.
    assert set(registro) == {"id", "classe_tarefa", "ciclo", "percentual", "criado_em"}


def test_a_cota_exposta_e_so_percentual(aluno):
    resposta = cliente(aluno).get("/api/v1/limites/uso/")

    assert resposta.status_code == 200
    assert set(resposta.json()) == {
        "ciclo",
        "limite_percentual",
        "consumido_percentual",
        "disponivel_percentual",
        "bloqueado",
    }


@pytest.mark.parametrize("codigo", ["PRISMA", "PRISMA_PRO", "PRISMA_ULTRA"])
def test_a_conta_sempre_le_cem_por_cento_qualquer_que_seja_o_plano(
    aluno, instituicao, codigo
):
    """O nucleo da regra: o teto na tela e 100 em todos os planos."""
    AssinaturaInstituicao.objects.create(
        instituicao=instituicao, plano=PlanoInstitucional.objects.get(codigo=codigo)
    )

    resposta = cliente(aluno).get("/api/v1/limites/uso/")

    assert resposta.json()["limite_percentual"] == "100.0000"


def test_o_mesmo_uso_pesa_menos_num_plano_maior(aluno, instituicao):
    """Ultra nao mostra um numero maior: mostra o mesmo uso ocupando menos."""
    AssinaturaInstituicao.objects.create(
        instituicao=instituicao,
        plano=PlanoInstitucional.objects.get(codigo="PRISMA_ULTRA"),
    )
    registrar_uso(
        usuario=aluno,
        percentual=Decimal("271"),
        fornecedor="provedor-a",
        modelo="modelo-a",
        classe_tarefa="TUTORIA",
        referencia=ChamadaIA.objects.create(instituicao=instituicao, usuario=aluno),
    )

    lido = cota_da_conta(estado_cota(aluno))

    # 271 unidades internas sao exatamente os 100% de quem esta no Ultra.
    assert lido.consumido_percentual == Decimal("100.0000")
    assert lido.disponivel_percentual == Decimal("0.0000")


def test_o_estouro_de_uma_chamada_nao_passa_de_cem_na_tela(aluno, instituicao):
    for percentual in (Decimal("90"), Decimal("30")):
        registrar_uso(
            usuario=aluno,
            percentual=percentual,
            fornecedor="provedor-a",
            modelo="modelo-a",
            classe_tarefa="TUTORIA",
            referencia=ChamadaIA.objects.create(instituicao=instituicao, usuario=aluno),
        )

    lido = cota_da_conta(estado_cota(aluno))

    assert lido.consumido_percentual == Decimal("100.0000")
    assert lido.bloqueado is True
    # Internamente o estouro continua registrado, para a contabilidade.
    assert estado_cota(aluno).consumido_percentual == Decimal("120")


def test_o_historico_vem_na_mesma_regua_da_cota(aluno, instituicao):
    AssinaturaInstituicao.objects.create(
        instituicao=instituicao,
        plano=PlanoInstitucional.objects.get(codigo="PRISMA_PRO"),
    )
    registrar_uso(
        usuario=aluno,
        percentual=Decimal("17.1"),
        fornecedor="provedor-a",
        modelo="modelo-a",
        classe_tarefa="RESUMO",
        referencia=ChamadaIA.objects.create(instituicao=instituicao, usuario=aluno),
    )

    resposta = cliente(aluno).get("/api/v1/limites/uso/historico/")

    # 17,1 de uma capacidade de 171 sao 10% da conta.
    assert resposta.json()["results"][0]["percentual"] == "10.0000"
