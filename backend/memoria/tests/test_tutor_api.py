from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from contas.models import Instituicao, Perfil
from limites.models import AssinaturaInstituicao, PlanoInstitucional
from memoria.models import Conversa, PapelMensagem

pytestmark = pytest.mark.django_db


def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


@pytest.fixture
def instituicao(db):
    return Instituicao.objects.create(
        nome="Escola Tutor API", documento="00.000.000/0001-41"
    )


@pytest.fixture
def aluno(db, instituicao):
    return get_user_model().objects.create_user(
        email="aluno-tutor-api@teste.com",
        password="senha-segura-123",
        instituicao=instituicao,
        perfil=Perfil.ALUNO,
    )


@pytest.fixture
def professor(db, instituicao):
    return get_user_model().objects.create_user(
        email="professor-tutor-api@teste.com",
        password="senha-segura-123",
        instituicao=instituicao,
        perfil=Perfil.PROFESSOR,
    )


@pytest.fixture
def outro_aluno(db):
    escola = Instituicao.objects.create(
        nome="Outra Escola Tutor", documento="00.000.000/0001-42"
    )
    return get_user_model().objects.create_user(
        email="outro-aluno-tutor-api@teste.com",
        password="senha-segura-123",
        instituicao=escola,
        perfil=Perfil.ALUNO,
    )


def test_aluno_cria_conversa_e_lista_so_as_proprias(aluno):
    resposta = cliente(aluno).post(
        "/api/v1/memoria/conversas/",
        {"titulo": "Funções", "disciplina": "matematica", "topico": "2º grau"},
        format="json",
    )

    assert resposta.status_code == 201
    conversa_id = resposta.data["id"]
    listagem = cliente(aluno).get("/api/v1/memoria/conversas/")
    assert listagem.status_code == 200
    assert [item["id"] for item in listagem.data["results"]] == [conversa_id]


def test_aluno_envia_mensagem_e_persiste_resposta_do_tutor(aluno):
    conversa = Conversa.objects.create(
        aluno=aluno, titulo="Dúvida", disciplina="matematica", topico="funções"
    )

    resposta = cliente(aluno).post(
        f"/api/v1/memoria/conversas/{conversa.id}/mensagens/",
        {"conteudo": "Como resolvo uma função do segundo grau?"},
        format="json",
    )

    assert resposta.status_code == 201
    assert conversa.mensagens.filter(papel=PapelMensagem.ALUNO).count() == 1
    assert conversa.mensagens.filter(papel=PapelMensagem.TUTOR).count() == 1
    assert resposta.data["mensagem_tutor"]["papel"] == PapelMensagem.TUTOR


def test_mensagem_vazia_e_rejeitada(aluno):
    conversa = Conversa.objects.create(aluno=aluno, titulo="Dúvida")

    resposta = cliente(aluno).post(
        f"/api/v1/memoria/conversas/{conversa.id}/mensagens/",
        {"conteudo": "   "},
        format="json",
    )

    assert resposta.status_code == 400
    assert conversa.mensagens.count() == 0


def test_professor_nao_cria_conversa(aluno, professor):
    resposta = cliente(professor).post(
        "/api/v1/memoria/conversas/", {"titulo": "não"}, format="json"
    )

    assert resposta.status_code == 403


def test_aluno_de_outro_tenant_recebe_404(aluno, outro_aluno):
    conversa = Conversa.objects.create(aluno=aluno, titulo="Privada")

    resposta = cliente(outro_aluno).post(
        f"/api/v1/memoria/conversas/{conversa.id}/mensagens/",
        {"conteudo": "tentativa"},
        format="json",
    )

    assert resposta.status_code == 404


def test_limite_excedido_nao_cria_resposta_do_tutor(aluno):
    plano = PlanoInstitucional.objects.get(codigo="PRISMA")
    plano.limite_percentual_por_conta = Decimal("0")
    plano.save(update_fields=["limite_percentual_por_conta"])
    AssinaturaInstituicao.objects.create(instituicao=aluno.instituicao, plano=plano)
    conversa = Conversa.objects.create(aluno=aluno, titulo="Bloqueada")

    resposta = cliente(aluno).post(
        f"/api/v1/memoria/conversas/{conversa.id}/mensagens/",
        {"conteudo": "não deve responder"},
        format="json",
    )

    assert resposta.status_code == 422
    assert conversa.mensagens.filter(papel=PapelMensagem.TUTOR).count() == 0


def test_aluno_le_e_atualiza_configuracao_do_tutor(aluno):
    inicial = cliente(aluno).get("/api/v1/memoria/tutor/configuracao/")
    assert inicial.status_code == 200
    assert inicial.data["estilo"] == "SOCRATICO"

    resposta = cliente(aluno).patch(
        "/api/v1/memoria/tutor/configuracao/",
        {
            "estilo": "DIRETO",
            "dificuldade": "DIFICIL",
            "tamanho_resposta": "DETALHADA",
            "resposta_audio": True,
        },
        format="json",
    )

    assert resposta.status_code == 200
    assert resposta.data["estilo"] == "DIRETO"
    assert resposta.data["resposta_audio"] is True


def test_professor_nao_le_configuracao_do_tutor(professor):
    resposta = cliente(professor).get("/api/v1/memoria/tutor/configuracao/")

    assert resposta.status_code == 403
