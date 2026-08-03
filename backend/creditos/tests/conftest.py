import pytest
from django.apps import apps
from django.contrib.auth import get_user_model

Instituicao = apps.get_model("contas", "Instituicao")
Usuario = get_user_model()


@pytest.fixture
def instituicao(db):
    return Instituicao.objects.create(
        nome="Escola Teste", documento="00.000.000/0001-01"
    )


@pytest.fixture
def aluno(db, instituicao):
    return Usuario.objects.create(
        email="aluno@teste.com", instituicao=instituicao, perfil="ALUNO"
    )


@pytest.fixture
def outro_aluno(db, instituicao):
    return Usuario.objects.create(
        email="outro@teste.com", instituicao=instituicao, perfil="ALUNO"
    )


@pytest.fixture
def diretor(db, instituicao):
    return Usuario.objects.create(
        email="diretor@teste.com", instituicao=instituicao, perfil="DIRETOR"
    )
