import pytest
from django.contrib.auth import get_user_model

from academico.models import Disciplina, Turma
from contas.models import Instituicao, Perfil


@pytest.fixture
def instituicao(db):
    return Instituicao.objects.create(
        nome="Escola Conteudo", documento="00.000.000/0001-10"
    )


@pytest.fixture
def outra_instituicao(db):
    return Instituicao.objects.create(
        nome="Outra Conteudo", documento="00.000.000/0001-11"
    )


@pytest.fixture
def professor(db, instituicao):
    return get_user_model().objects.create_user(
        email="professor-conteudo@teste.com", password="senha", instituicao=instituicao, perfil=Perfil.PROFESSOR
    )


@pytest.fixture
def outro_professor(db, instituicao):
    return get_user_model().objects.create_user(
        email="outro-professor-conteudo@teste.com", password="senha", instituicao=instituicao, perfil=Perfil.PROFESSOR
    )


@pytest.fixture
def diretor(db, instituicao):
    return get_user_model().objects.create_user(
        email="diretor-conteudo@teste.com", password="senha", instituicao=instituicao, perfil=Perfil.DIRETOR
    )


@pytest.fixture
def aluno(db, instituicao):
    return get_user_model().objects.create_user(
        email="aluno-conteudo@teste.com", password="senha", instituicao=instituicao, perfil=Perfil.ALUNO
    )


@pytest.fixture
def turma_disciplina(instituicao, professor):
    disciplina = Disciplina.objects.create(instituicao=instituicao, nome="Portugues")
    turma = Turma.objects.create(
        instituicao=instituicao, nome="Turma Conteudo", disciplina=disciplina, professor_responsavel=professor
    )
    return turma, disciplina
