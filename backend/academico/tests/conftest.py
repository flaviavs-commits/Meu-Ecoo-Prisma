import pytest
from django.contrib.auth import get_user_model

from contas.models import Instituicao, Perfil


@pytest.fixture
def instituicao(db):
    return Instituicao.objects.create(
        nome="Escola Academica", documento="00.000.000/0001-08"
    )


@pytest.fixture
def outra_instituicao(db):
    return Instituicao.objects.create(
        nome="Outra Academica", documento="00.000.000/0001-09"
    )


@pytest.fixture
def professor(db, instituicao):
    return get_user_model().objects.create_user(
        email="professor-academico@teste.com",
        password="senha-segura-123",
        instituicao=instituicao,
        perfil=Perfil.PROFESSOR,
    )


@pytest.fixture
def diretor(db, instituicao):
    return get_user_model().objects.create_user(
        email="diretor-academico@teste.com",
        password="senha-segura-123",
        instituicao=instituicao,
        perfil=Perfil.DIRETOR,
    )


@pytest.fixture
def outro_professor(db, instituicao):
    return get_user_model().objects.create_user(
        email="outro-professor-academico@teste.com",
        password="senha-segura-123",
        instituicao=instituicao,
        perfil=Perfil.PROFESSOR,
    )


@pytest.fixture
def aluno(db, instituicao):
    return get_user_model().objects.create_user(
        email="aluno-academico@teste.com",
        password="senha-segura-123",
        instituicao=instituicao,
        perfil=Perfil.ALUNO,
    )


@pytest.fixture
def colega(db, instituicao):
    return get_user_model().objects.create_user(
        email="colega-academico@teste.com",
        password="senha-segura-123",
        instituicao=instituicao,
        perfil=Perfil.ALUNO,
    )
