import pytest
from django.contrib.auth import get_user_model

from contas.models import Instituicao, Perfil


@pytest.fixture
def instituicao(db):
    return Instituicao.objects.create(nome="Escola dos Avisos", documento="00.000.000/0001-10")


def _conta(instituicao, email, perfil):
    return get_user_model().objects.create_user(
        email=email, password="senha-segura-123", instituicao=instituicao, perfil=perfil
    )


@pytest.fixture
def professor(db, instituicao):
    return _conta(instituicao, "professor-avisos@teste.com", Perfil.PROFESSOR)


@pytest.fixture
def diretor(db, instituicao):
    return _conta(instituicao, "diretor-avisos@teste.com", Perfil.DIRETOR)


@pytest.fixture
def aluno(db, instituicao):
    return _conta(instituicao, "aluno-avisos@teste.com", Perfil.ALUNO)
