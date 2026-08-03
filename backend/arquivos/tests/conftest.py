import pytest
from django.contrib.auth import get_user_model

from contas.models import Instituicao, Perfil


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    settings.ARQUIVO_MAX_BYTES = 10_000
    settings.ARQUIVO_COTA_INSTITUICAO_BYTES = 100_000
    return tmp_path


@pytest.fixture
def instituicao(db):
    return Instituicao.objects.create(
        nome="Escola Arquivos", documento="00.000.000/0001-06"
    )


@pytest.fixture
def aluno(db, instituicao):
    return get_user_model().objects.create_user(
        email="aluno-arquivo@teste.com",
        password="senha-segura-123",
        instituicao=instituicao,
        perfil=Perfil.ALUNO,
    )


@pytest.fixture
def outra_instituicao(db):
    return Instituicao.objects.create(
        nome="Outra Escola Arquivos", documento="00.000.000/0001-07"
    )


@pytest.fixture
def outro_aluno(db, outra_instituicao):
    return get_user_model().objects.create_user(
        email="outro-arquivo@teste.com",
        password="senha-segura-123",
        instituicao=outra_instituicao,
        perfil=Perfil.ALUNO,
    )
