import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from contas.models import Instituicao, Perfil
from memoria.models import Conversa

pytestmark = pytest.mark.django_db


def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


@pytest.fixture
def aluno(db):
    instituicao = Instituicao.objects.create(
        nome="Escola Dashboard", documento="00.000.000/0001-71"
    )
    return get_user_model().objects.create_user(
        email="aluno-dashboard@teste.com",
        password="senha-segura-123",
        instituicao=instituicao,
        perfil=Perfil.ALUNO,
    )


def test_dashboard_do_aluno_retorna_metricas_e_cota(aluno):
    Conversa.objects.create(aluno=aluno, titulo="Primeira sessão")

    resposta = cliente(aluno).get("/api/v1/aluno/dashboard/")

    assert resposta.status_code == 200
    assert resposta.data["metricas"]["sessoes"] == 1
    assert resposta.data["cota"]["limite_percentual"] == "100.0000"


def test_dashboard_nao_e_acessivel_por_perfil_administrativo(aluno):
    aluno.perfil = Perfil.DIRETOR
    aluno.save(update_fields=["perfil"])

    resposta = cliente(aluno).get("/api/v1/aluno/dashboard/")

    assert resposta.status_code == 403
