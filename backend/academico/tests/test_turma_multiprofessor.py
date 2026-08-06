"""Uma turma tem N professores; um professor leciona em N turmas."""
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from academico.matriculas import matricular
from academico.models import Disciplina, Turma
from academico.notas import (
    AcademicoPermissaoError,
    aprovar_nota,
    consultar_notas,
    lancar_nota,
)
from contas.models import Perfil

pytestmark = pytest.mark.django_db


@pytest.fixture
def segundo_professor(instituicao):
    return get_user_model().objects.create_user(
        "professor2@escola.test", "senha", instituicao=instituicao, perfil=Perfil.PROFESSOR
    )


@pytest.fixture
def turma_com_dois_professores(instituicao, professor, segundo_professor):
    disciplina = Disciplina.objects.create(instituicao=instituicao, nome="Historia")
    turma = Turma.objects.create(
        instituicao=instituicao,
        nome="9o ano B",
        disciplina=disciplina,
        professor_responsavel=professor,
    )
    turma.professores.add(professor, segundo_professor)
    return turma, disciplina


def test_leciona_reconhece_titular_e_corpo_docente(
    turma_com_dois_professores, professor, segundo_professor, aluno
):
    turma, _ = turma_com_dois_professores

    assert turma.leciona(professor) is True
    assert turma.leciona(segundo_professor) is True
    assert turma.leciona(aluno) is False


def test_professor_sem_titularidade_lanca_nota_na_turma_em_que_leciona(
    turma_com_dois_professores, segundo_professor, diretor, aluno
):
    turma, disciplina = turma_com_dois_professores
    matricular(turma=turma, aluno=aluno, criado_por=diretor)

    nota = lancar_nota(
        turma=turma,
        disciplina=disciplina,
        aluno=aluno,
        avaliacao="Prova 1",
        valor=Decimal("8.00"),
        ator=segundo_professor,
    )

    assert nota.criado_por == segundo_professor


def test_professor_de_fora_da_turma_continua_barrado(
    turma_com_dois_professores, instituicao, diretor, aluno
):
    turma, disciplina = turma_com_dois_professores
    matricular(turma=turma, aluno=aluno, criado_por=diretor)
    forasteiro = get_user_model().objects.create_user(
        "forasteiro@escola.test", "senha", instituicao=instituicao, perfil=Perfil.PROFESSOR
    )

    with pytest.raises(AcademicoPermissaoError):
        lancar_nota(
            turma=turma,
            disciplina=disciplina,
            aluno=aluno,
            avaliacao="Prova 1",
            valor=Decimal("8.00"),
            ator=forasteiro,
        )


def test_consulta_do_professor_alcanca_turma_em_que_so_leciona(
    turma_com_dois_professores, professor, segundo_professor, diretor, aluno
):
    turma, disciplina = turma_com_dois_professores
    matricular(turma=turma, aluno=aluno, criado_por=diretor)
    lancar_nota(
        turma=turma,
        disciplina=disciplina,
        aluno=aluno,
        avaliacao="Prova 1",
        valor=Decimal("7.00"),
        ator=professor,
    )

    assert consultar_notas(usuario=segundo_professor).count() == 1


def test_professor_do_corpo_docente_aprova_nota_do_colega(
    turma_com_dois_professores, professor, segundo_professor, diretor, aluno
):
    turma, disciplina = turma_com_dois_professores
    matricular(turma=turma, aluno=aluno, criado_por=diretor)
    nota = lancar_nota(
        turma=turma,
        disciplina=disciplina,
        aluno=aluno,
        avaliacao="Prova 1",
        valor=Decimal("9.00"),
        ator=professor,
    )

    aprovada = aprovar_nota(
        nota=nota, ator=segundo_professor, confirmacao=True, motivo="revisao em conselho"
    )

    assert aprovada.oficial is True


def test_um_professor_leciona_em_varias_turmas(instituicao, professor, segundo_professor):
    disciplina = Disciplina.objects.create(instituicao=instituicao, nome="Geografia")
    primeira = Turma.objects.create(instituicao=instituicao, nome="1a", disciplina=disciplina)
    segunda = Turma.objects.create(instituicao=instituicao, nome="2a", disciplina=disciplina)
    primeira.professores.add(segundo_professor)
    segunda.professores.add(segundo_professor)

    assert segundo_professor.turmas_lecionadas.count() == 2
