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


def test_filtro_de_data_nao_usa_datetime_naive(aluno, recwarn):
    """Regressao: `datetime.fromisoformat` devolvia naive com `USE_TZ=True`,
    emitindo `RuntimeWarning` a cada request e deixando o fuso implicito."""
    import warnings

    warnings.simplefilter("always")
    resposta = cliente(aluno).get("/api/v1/aluno/agenda/?de=2026-08-01&ate=2026-08-31")

    assert resposta.status_code == 200
    assert not [aviso for aviso in recwarn if "naive datetime" in str(aviso.message)]


def test_filtro_aceita_data_pura_e_data_com_fuso(aluno):
    apenas_data = cliente(aluno).get("/api/v1/aluno/agenda/?de=2026-08-01")
    com_fuso = cliente(aluno).get("/api/v1/aluno/agenda/?de=2026-08-01T00:00:00Z")

    assert apenas_data.status_code == 200
    assert com_fuso.status_code == 200


def test_filtro_com_data_invalida_responde_400(aluno):
    resposta = cliente(aluno).get("/api/v1/aluno/agenda/?de=nao-e-data")

    assert resposta.status_code == 400
