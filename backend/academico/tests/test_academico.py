from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from django.test.utils import CaptureQueriesContext
from django.db import connection

from academico.agregados import media_da_turma
from academico.matriculas import listar_alunos, matricular
from academico.models import Disciplina, Falta, Matricula, Nota, Turma
from academico.notas import (
    AcademicoPermissaoError,
    NotaForaDaFaixaError,
    atualizar_nota,
    consultar_notas,
    lancar_nota,
    registrar_falta,
)
from contas.auditoria import RegistroDeAuditoria

pytestmark = pytest.mark.django_db


def turma_com_disciplina(instituicao, professor):
    disciplina = Disciplina.objects.create(instituicao=instituicao, nome="Matematica")
    turma = Turma.objects.create(
        instituicao=instituicao,
        nome="9o ano A",
        disciplina=disciplina,
        professor_responsavel=professor,
    )
    return turma, disciplina


def test_cria_turma_matricula_e_lista_alunos(instituicao, professor, diretor, aluno):
    turma, _ = turma_com_disciplina(instituicao, professor)
    matricular(turma=turma, aluno=aluno, criado_por=diretor)

    assert list(listar_alunos(turma)) == [aluno]


def test_matricula_duplicada_e_recusada_pelo_banco(instituicao, professor, diretor, aluno):
    turma, _ = turma_com_disciplina(instituicao, professor)
    matricular(turma=turma, aluno=aluno, criado_por=diretor)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Matricula.objects.create(turma=turma, aluno=aluno)


def test_professor_lanca_nota_na_propria_turma(instituicao, professor, diretor, aluno):
    turma, disciplina = turma_com_disciplina(instituicao, professor)
    matricular(turma=turma, aluno=aluno, criado_por=diretor)
    nota = lancar_nota(
        turma=turma,
        disciplina=disciplina,
        aluno=aluno,
        valor=Decimal("8"),
        avaliacao="prova 1",
        ator=professor,
    )

    assert nota.valor == Decimal("8")


def test_professor_de_outra_turma_recebe_403(instituicao, professor, diretor, outro_professor, aluno):
    turma, disciplina = turma_com_disciplina(instituicao, professor)
    matricular(turma=turma, aluno=aluno, criado_por=diretor)

    with pytest.raises(AcademicoPermissaoError):
        lancar_nota(
            turma=turma,
            disciplina=disciplina,
            aluno=aluno,
            valor=Decimal("8"),
            avaliacao="prova 1",
            ator=outro_professor,
        )


def test_professor_de_outra_instituicao_recebe_404(
    instituicao, outra_instituicao, professor, aluno
):
    turma, disciplina = turma_com_disciplina(instituicao, professor)
    outro = outra_instituicao.usuarios.create_user(
        email="professor-fora@teste.com",
        password="senha",
        instituicao=outra_instituicao,
        perfil="PROFESSOR",
    )

    with pytest.raises(AcademicoPermissaoError) as erro:
        lancar_nota(
            turma=turma,
            disciplina=disciplina,
            aluno=aluno,
            valor=Decimal("8"),
            avaliacao="prova 1",
            ator=outro,
        )

    assert erro.value.codigo == "fora_da_instituicao"


def test_aluno_consulta_so_as_proprias_notas(instituicao, professor, diretor, aluno, colega):
    turma, disciplina = turma_com_disciplina(instituicao, professor)
    matricular(turma=turma, aluno=aluno, criado_por=diretor)
    matricular(turma=turma, aluno=colega, criado_por=diretor)
    lancar_nota(
        turma=turma, disciplina=disciplina, aluno=aluno, valor=Decimal("8"), avaliacao="p1", ator=professor
    )
    lancar_nota(
        turma=turma, disciplina=disciplina, aluno=colega, valor=Decimal("6"), avaliacao="p1", ator=professor
    )

    notas = consultar_notas(usuario=aluno)

    assert list(notas) == list(Nota.objects.filter(aluno=aluno))


def test_aluno_nao_consulta_nota_de_colega(instituicao, professor, diretor, aluno, colega):
    turma, disciplina = turma_com_disciplina(instituicao, professor)
    matricular(turma=turma, aluno=colega, criado_por=diretor)
    nota = lancar_nota(
        turma=turma, disciplina=disciplina, aluno=colega, valor=Decimal("6"), avaliacao="p1", ator=professor
    )

    with pytest.raises(AcademicoPermissaoError):
        consultar_notas(usuario=aluno, aluno_alvo=colega)

    assert nota.aluno_id == colega.id


def test_nota_fora_da_faixa_e_recusada(instituicao, professor, diretor, aluno):
    turma, disciplina = turma_com_disciplina(instituicao, professor)
    matricular(turma=turma, aluno=aluno, criado_por=diretor)

    with pytest.raises(NotaForaDaFaixaError):
        lancar_nota(
            turma=turma, disciplina=disciplina, aluno=aluno, valor=Decimal("11"), avaliacao="p1", ator=professor
        )


def test_falta_duplicada_no_mesmo_dia_e_recusada(instituicao, professor, diretor, aluno):
    from datetime import date

    turma, _ = turma_com_disciplina(instituicao, professor)
    matricular(turma=turma, aluno=aluno, criado_por=diretor)
    registrar_falta(turma=turma, aluno=aluno, data=date(2026, 8, 3), ator=professor)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Falta.objects.create(turma=turma, aluno=aluno, data=date(2026, 8, 3))


def test_alteracao_de_nota_grava_auditoria(instituicao, professor, diretor, aluno):
    turma, disciplina = turma_com_disciplina(instituicao, professor)
    matricular(turma=turma, aluno=aluno, criado_por=diretor)
    nota = lancar_nota(
        turma=turma, disciplina=disciplina, aluno=aluno, valor=Decimal("6"), avaliacao="p1", ator=professor
    )

    atualizar_nota(nota=nota, novo_valor=Decimal("7"), ator=professor)

    assert RegistroDeAuditoria.objects.filter(
        objeto_tipo="Nota", objeto_id=str(nota.id), acao="alterar_nota", motivo__contains="6"
    ).exists()


def test_media_da_turma_e_calculada_no_banco(instituicao, professor, diretor, aluno, colega):
    turma, disciplina = turma_com_disciplina(instituicao, professor)
    matricular(turma=turma, aluno=aluno, criado_por=diretor)
    matricular(turma=turma, aluno=colega, criado_por=diretor)
    lancar_nota(turma=turma, disciplina=disciplina, aluno=aluno, valor=Decimal("8"), avaliacao="p1", ator=professor)
    lancar_nota(turma=turma, disciplina=disciplina, aluno=colega, valor=Decimal("6"), avaliacao="p1", ator=professor)

    with CaptureQueriesContext(connection) as queries:
        media = media_da_turma(turma, disciplina=disciplina)

    assert media == Decimal("7")
    assert len(queries) == 1
