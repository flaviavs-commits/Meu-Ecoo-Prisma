from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from contas.models import Instituicao, Perfil
from conteudo.models import Simulado, StatusSimulado
from limites.models import AssinaturaInstituicao, PlanoInstitucional

pytestmark = pytest.mark.django_db


def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


@pytest.fixture
def instituicao(db):
    return Instituicao.objects.create(
        nome="Escola Simulados", documento="00.000.000/0001-61"
    )


@pytest.fixture
def aluno(db, instituicao):
    return get_user_model().objects.create_user(
        email="aluno-simulado@teste.com",
        password="senha-segura-123",
        instituicao=instituicao,
        perfil=Perfil.ALUNO,
    )


@pytest.fixture
def outro_aluno(db):
    escola = Instituicao.objects.create(
        nome="Outra Escola Simulados", documento="00.000.000/0001-62"
    )
    return get_user_model().objects.create_user(
        email="outro-aluno-simulado@teste.com",
        password="senha-segura-123",
        instituicao=escola,
        perfil=Perfil.ALUNO,
    )


def test_aluno_gera_simulado_e_nao_recebe_gabarito(aluno):
    resposta = cliente(aluno).post(
        "/api/v1/conteudo/simulados/gerar/",
        {
            "disciplina": "Português",
            "estilo": "ENEM",
            "quantidade": 3,
            "foco_dificuldades": True,
            "correcao_comentada": True,
        },
        format="json",
    )

    assert resposta.status_code == 201
    simulado = Simulado.objects.get(pk=resposta.data["id"])
    assert simulado.status == StatusSimulado.EM_ANDAMENTO
    assert simulado.questoes.count() == 3
    assert "gabarito" not in resposta.data["questoes"][0]
    assert aluno.consumos_ia.count() == 1


def test_aluno_responde_e_finaliza_com_percentual(aluno):
    resposta = cliente(aluno).post(
        "/api/v1/conteudo/simulados/gerar/",
        {"disciplina": "História", "quantidade": 1},
        format="json",
    )
    simulado_id = resposta.data["id"]
    questao_id = resposta.data["questoes"][0]["id"]
    gabarito = Simulado.objects.get(pk=simulado_id).questoes.first().gabarito

    marcar = cliente(aluno).post(
        f"/api/v1/conteudo/simulados/{simulado_id}/questoes/{questao_id}/responder/",
        {"alternativa": gabarito},
        format="json",
    )
    finalizar = cliente(aluno).post(
        f"/api/v1/conteudo/simulados/{simulado_id}/finalizar/",
        {},
        format="json",
    )

    assert marcar.status_code == 200
    assert finalizar.status_code == 200
    assert finalizar.data["resultado_percentual"] == "100.0000"
    assert finalizar.data["questoes"][0]["gabarito"] == gabarito
    assert Simulado.objects.get(pk=simulado_id).status == StatusSimulado.CONCLUIDO


def test_marcar_sempre_a_mesma_alternativa_nao_zera_o_simulado(aluno):
    """Regressao: com `gabarito="A"` em todas as questoes, responder "A" em tudo
    dava 100% e esse percentual ia para o progresso por materia do dashboard."""
    resposta = cliente(aluno).post(
        "/api/v1/conteudo/simulados/gerar/",
        {"disciplina": "História", "quantidade": 4},
        format="json",
    )
    simulado_id = resposta.data["id"]
    for questao in resposta.data["questoes"]:
        cliente(aluno).post(
            f"/api/v1/conteudo/simulados/{simulado_id}/questoes/{questao['id']}/responder/",
            {"alternativa": "A"},
            format="json",
        )

    finalizar = cliente(aluno).post(
        f"/api/v1/conteudo/simulados/{simulado_id}/finalizar/", {}, format="json"
    )

    assert finalizar.data["resultado_percentual"] == "25.0000"


def test_aluno_nao_acessa_simulado_de_outro_tenant(aluno, outro_aluno):
    resposta = cliente(outro_aluno).post(
        "/api/v1/conteudo/simulados/gerar/",
        {"disciplina": "História", "quantidade": 1},
        format="json",
    )
    simulado = Simulado.objects.get(pk=resposta.data["id"])

    externo = cliente(aluno).get(f"/api/v1/conteudo/simulados/{simulado.id}/")

    assert externo.status_code == 404


def test_simulado_bloqueado_sem_percentual_disponivel(aluno):
    plano = PlanoInstitucional.objects.get(codigo="PRISMA")
    plano.limite_percentual_por_conta = Decimal("0")
    plano.save(update_fields=["limite_percentual_por_conta"])
    AssinaturaInstituicao.objects.create(instituicao=aluno.instituicao, plano=plano)

    resposta = cliente(aluno).post(
        "/api/v1/conteudo/simulados/gerar/",
        {"disciplina": "História", "quantidade": 1},
        format="json",
    )

    assert resposta.status_code == 422
