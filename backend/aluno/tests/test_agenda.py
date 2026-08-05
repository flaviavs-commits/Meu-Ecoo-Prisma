import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from contas.models import Instituicao, Perfil

pytestmark = pytest.mark.django_db


@pytest.fixture
def aluno(db):
    instituicao = Instituicao.objects.create(
        nome="Escola Agenda", documento="00.000.000/0001-72"
    )
    return get_user_model().objects.create_user(
        email="aluno-agenda@teste.com",
        password="senha-segura-123",
        instituicao=instituicao,
        perfil=Perfil.ALUNO,
    )


def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


def test_aluno_cria_lista_e_conclui_item_da_agenda(aluno):
    resposta = cliente(aluno).post(
        "/api/v1/aluno/agenda/",
        {
            "titulo": "Revisar funções",
            "disciplina": "Matemática",
            "agendado_para": "2026-08-07T18:00:00Z",
        },
        format="json",
    )

    assert resposta.status_code == 201
    agenda_id = resposta.data["id"]
    assert len(cliente(aluno).get("/api/v1/aluno/agenda/").data) == 1

    concluido = cliente(aluno).patch(
        f"/api/v1/aluno/agenda/{agenda_id}/",
        {"status": "CONCLUIDA"},
        format="json",
    )
    assert concluido.status_code == 200
    assert concluido.data["status"] == "CONCLUIDA"


def test_filtro_de_agenda_invalido_retorna_400(aluno):
    resposta = cliente(aluno).get("/api/v1/aluno/agenda/?de=nao-e-data")

    assert resposta.status_code == 400
    assert "Data de agenda invalida" in resposta.data["erro"]["mensagem"]
