import pytest
from django.contrib.auth import get_user_model

from contas.models import Instituicao, Perfil


@pytest.fixture
def instituicao(db):
    return Instituicao.objects.create(nome="Escola dos Custos", documento="00.000.000/0001-11")


@pytest.fixture
def aluno(db, instituicao):
    return get_user_model().objects.create_user(
        email="aluno-custos@teste.com",
        password="senha-segura-123",
        instituicao=instituicao,
        perfil=Perfil.ALUNO,
    )
