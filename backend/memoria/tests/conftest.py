import pytest
from django.contrib.auth import get_user_model

from contas.models import Instituicao, Perfil


@pytest.fixture
def instituicao(db):
    return Instituicao.objects.create(
        nome="Escola Memoria", documento="00.000.000/0001-04"
    )


@pytest.fixture
def aluno(db, instituicao):
    return get_user_model().objects.create_user(
        email="aluno-memoria@teste.com",
        password="senha-segura-123",
        instituicao=instituicao,
        perfil=Perfil.ALUNO,
    )


@pytest.fixture
def professor(db, instituicao):
    return get_user_model().objects.create_user(
        email="professor-memoria@teste.com",
        password="senha-segura-123",
        instituicao=instituicao,
        perfil=Perfil.PROFESSOR,
    )


@pytest.fixture
def diretor(db, instituicao):
    return get_user_model().objects.create_user(
        email="diretor-memoria@teste.com",
        password="senha-segura-123",
        instituicao=instituicao,
        perfil=Perfil.DIRETOR,
    )


@pytest.fixture
def outro_aluno(db):
    outra = Instituicao.objects.create(
        nome="Outra Escola", documento="00.000.000/0001-05"
    )
    return get_user_model().objects.create_user(
        email="aluno-outra-memoria@teste.com",
        password="senha-segura-123",
        instituicao=outra,
        perfil=Perfil.ALUNO,
    )
