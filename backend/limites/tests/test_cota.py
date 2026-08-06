from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from contas.models import Instituicao, Perfil, TipoInstituicao
from ia.models import ChamadaIA
from limites.ciclo import ciclo_atual
from limites.excecoes import LimiteDeUsoExcedidoError
from limites.servico import (
    autorizar_uso,
    estado_cota,
    obter_cota,
    registrar_uso,
    trava_cota,
)
from limites.models import (
    AssinaturaInstituicao,
    ConsumoIA,
    CotaImutavelError,
    PlanoInstitucional,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def plano_prisma(db):
    plano, _ = PlanoInstitucional.objects.get_or_create(
        codigo="PRISMA",
        defaults={
            "nome": "Prisma",
            "preco_por_conta": Decimal("68.97"),
            "limite_percentual_por_conta": Decimal("100"),
        },
    )
    return plano


@pytest.fixture
def provedora(db):
    instituicao, _ = Instituicao.objects.get_or_create(
        codigo="VITIS_SOULS",
        defaults={"nome": "Vitis Souls", "tipo": TipoInstituicao.PROVEDORA},
    )
    return get_user_model().objects.create_superuser(
        email="provider-limites@teste.com",
        password="senha-segura-123",
        instituicao=instituicao,
    )


def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


def chamada(aluno):
    return ChamadaIA.objects.create(instituicao=aluno.instituicao, usuario=aluno)


def test_cota_nasce_com_limite_total_e_saldo_disponivel(aluno, plano_prisma):
    AssinaturaInstituicao.objects.create(instituicao=aluno.instituicao, plano=plano_prisma)
    estado = estado_cota(aluno)

    assert estado.limite_percentual == Decimal("100")
    assert estado.consumido_percentual == Decimal("0")
    assert estado.disponivel_percentual == Decimal("100")
    assert estado.bloqueado is False


def test_uso_debita_percentual_e_preserva_fornecedor(aluno):
    referencia = chamada(aluno)
    registrar_uso(
        usuario=aluno,
        percentual=Decimal("12.3456"),
        fornecedor="provedor-teste",
        modelo="modelo-teste",
        classe_tarefa="TUTORIA",
        referencia=referencia,
    )

    estado = estado_cota(aluno)
    consumo = ConsumoIA.objects.get(usuario=aluno)
    assert estado.consumido_percentual == Decimal("12.3456")
    assert estado.disponivel_percentual == Decimal("87.6544")
    assert consumo.fornecedor == "provedor-teste"
    assert consumo.modelo == "modelo-teste"


def test_gate_bloqueia_cota_esgotada(aluno):
    plano = PlanoInstitucional.objects.get(codigo="PRISMA")
    plano.limite_percentual_por_conta = Decimal("10")
    plano.save(update_fields=["limite_percentual_por_conta"])
    AssinaturaInstituicao.objects.create(instituicao=aluno.instituicao, plano=plano)
    registrar_uso(
        usuario=aluno,
        percentual=Decimal("10"),
        fornecedor="falso",
        modelo="modelo",
        classe_tarefa="GERACAO",
        referencia=chamada(aluno),
    )

    with pytest.raises(LimiteDeUsoExcedidoError) as erro:
        with trava_cota(aluno):
            autorizar_uso(aluno)

    assert erro.value.codigo == "limite_uso_excedido"


def test_debito_que_ultrapassa_o_limite_e_registrado_e_bloqueia_a_proxima(aluno):
    """Regressao: recusar aqui perdia dinheiro.

    O percentual so chega a `registrar_uso` depois que o provedor respondeu, ou
    seja, depois que o custo virou fato. Recusar deixava o fornecedor cobrando
    e a nossa contabilidade sem registro. Agora o consumo entra, a conta fica
    negativa, e e o portao (`autorizar_uso`) que barra a chamada seguinte.
    """
    plano = PlanoInstitucional.objects.get(codigo="PRISMA")
    plano.limite_percentual_por_conta = Decimal("10")
    plano.save(update_fields=["limite_percentual_por_conta"])
    AssinaturaInstituicao.objects.create(instituicao=aluno.instituicao, plano=plano)
    registrar_uso(
        usuario=aluno,
        percentual=Decimal("9"),
        fornecedor="falso",
        modelo="modelo",
        classe_tarefa="TUTORIA",
        referencia=chamada(aluno),
    )

    registrar_uso(
        usuario=aluno,
        percentual=Decimal("2"),
        fornecedor="falso",
        modelo="modelo",
        classe_tarefa="TUTORIA",
        referencia=chamada(aluno),
    )

    estado = estado_cota(aluno)
    assert estado.consumido_percentual == Decimal("11")
    assert estado.disponivel_percentual == Decimal("-1")
    assert estado.bloqueado is True
    with pytest.raises(LimiteDeUsoExcedidoError):
        autorizar_uso(aluno)


def test_mesma_chamada_nao_debita_duas_vezes(aluno):
    referencia = chamada(aluno)
    primeiro = registrar_uso(
        usuario=aluno,
        percentual=Decimal("4"),
        fornecedor="falso",
        modelo="modelo",
        classe_tarefa="RESUMO",
        referencia=referencia,
    )
    segundo = registrar_uso(
        usuario=aluno,
        percentual=Decimal("9"),
        fornecedor="outro",
        modelo="outro",
        classe_tarefa="RESUMO",
        referencia=referencia,
    )

    assert segundo.pk == primeiro.pk
    assert ConsumoIA.objects.filter(usuario=aluno).count() == 1
    assert estado_cota(aluno).consumido_percentual == Decimal("4")


def test_consumo_e_append_only(aluno):
    consumo = registrar_uso(
        usuario=aluno,
        percentual=Decimal("1"),
        fornecedor="falso",
        modelo="modelo",
        classe_tarefa="TUTORIA",
        referencia=chamada(aluno),
    )
    consumo.percentual = Decimal("2")

    with pytest.raises(CotaImutavelError):
        consumo.save()
    with pytest.raises(CotaImutavelError):
        consumo.delete()


def test_aluno_consulta_apenas_a_propria_cota(aluno):
    resposta = cliente(aluno).get("/api/v1/limites/uso/")

    assert resposta.status_code == 200
    assert resposta.data == {
        "ciclo": ciclo_atual(),
        "limite_percentual": "100.0000",
        "consumido_percentual": "0.0000",
        "disponivel_percentual": "100.0000",
        "bloqueado": False,
    }


def test_catalogo_expoe_limites_e_precos_por_conta(aluno):
    resposta = cliente(aluno).get("/api/v1/limites/planos/")

    assert resposta.status_code == 200
    assert [(plano["codigo"], plano["limite_percentual_por_conta"]) for plano in resposta.data] == [
        ("PRISMA", "100.0000"),
        ("PRISMA_PRO", "171.0000"),
        ("PRISMA_ULTRA", "271.0000"),
    ]


def test_provider_pode_trocar_plano_com_motivo(aluno, provedora):
    plano = PlanoInstitucional.objects.get(codigo="PRISMA_PRO")
    resposta = cliente(provedora).patch(
        f"/api/v1/limites/instituicoes/{aluno.instituicao_id}/plano/",
        {"plano": plano.codigo, "motivo": "Upgrade para homologação"},
        format="json",
    )

    assert resposta.status_code == 200
    assert estado_cota(aluno).limite_percentual == Decimal("171")


def test_provider_exige_motivo_para_alterar_limite(aluno, provedora):
    plano = PlanoInstitucional.objects.get(codigo="PRISMA_PRO")
    resposta = cliente(provedora).patch(
        f"/api/v1/limites/instituicoes/{aluno.instituicao_id}/plano/",
        {"plano": plano.codigo, "motivo": "  "},
        format="json",
    )

    assert resposta.status_code == 400
    assert estado_cota(aluno).limite_percentual == Decimal("100")


def test_usuario_academico_nao_altera_limite(aluno):
    resposta = cliente(aluno).patch(
        f"/api/v1/limites/instituicoes/{aluno.instituicao_id}/plano/",
        {"plano": "PRISMA_PRO", "motivo": "tentativa"},
        format="json",
    )

    assert resposta.status_code == 403


def test_provider_nao_recebe_plano_comercial(provedora):
    resposta = cliente(provedora).patch(
        f"/api/v1/limites/instituicoes/{provedora.instituicao_id}/plano/",
        {"plano": "PRISMA_PRO", "motivo": "tentativa indevida"},
        format="json",
    )

    assert resposta.status_code == 400
