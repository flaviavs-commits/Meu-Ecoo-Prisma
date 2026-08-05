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


def test_diretor_enxerga_notas_de_turmas_de_varios_professores(
    instituicao, professor, outro_professor, diretor, aluno, colega
):
    """Diretor monitora a instituicao inteira, nao so uma turma/professor."""
    turma_a, disciplina_a = turma_com_disciplina(instituicao, professor)
    turma_b = Turma.objects.create(
        instituicao=instituicao, nome="9o ano B", disciplina=disciplina_a,
        professor_responsavel=outro_professor,
    )
    matricular(turma=turma_a, aluno=aluno, criado_por=diretor)
    matricular(turma=turma_b, aluno=colega, criado_por=diretor)
    lancar_nota(turma=turma_a, disciplina=disciplina_a, aluno=aluno, valor=Decimal("8"), avaliacao="p1", ator=professor)
    lancar_nota(turma=turma_b, disciplina=disciplina_a, aluno=colega, valor=Decimal("9"), avaliacao="p1", ator=outro_professor)

    notas_do_diretor = consultar_notas(usuario=diretor)

    assert set(notas_do_diretor.values_list("aluno_id", flat=True)) == {aluno.id, colega.id}


def test_dois_diretores_da_mesma_instituicao_enxergam_os_mesmos_dados(
    instituicao, professor, diretor, aluno
):
    """Varias contas de diretor da mesma instituicao monitoram a mesma coisa."""
    outro_diretor = type(diretor).objects.create_user(
        email="segundo-diretor@teste.com", password="senha-segura-123",
        instituicao=instituicao, perfil="DIRETOR",
    )
    turma, disciplina = turma_com_disciplina(instituicao, professor)
    matricular(turma=turma, aluno=aluno, criado_por=diretor)
    lancar_nota(turma=turma, disciplina=disciplina, aluno=aluno, valor=Decimal("7"), avaliacao="p1", ator=professor)

    notas_diretor_1 = set(consultar_notas(usuario=diretor).values_list("id", flat=True))
    notas_diretor_2 = set(consultar_notas(usuario=outro_diretor).values_list("id", flat=True))

    assert notas_diretor_1 == notas_diretor_2
    assert len(notas_diretor_1) == 1


def test_professor_com_varias_turmas_ve_notas_de_todas_elas(
    instituicao, professor, diretor, aluno, colega
):
    """1 professor pode ter varias turmas na mesma instituicao."""
    disciplina = Disciplina.objects.create(instituicao=instituicao, nome="Historia")
    turma_1 = Turma.objects.create(
        instituicao=instituicao, nome="7o ano A", disciplina=disciplina, professor_responsavel=professor,
    )
    turma_2 = Turma.objects.create(
        instituicao=instituicao, nome="8o ano A", disciplina=disciplina, professor_responsavel=professor,
    )
    matricular(turma=turma_1, aluno=aluno, criado_por=diretor)
    matricular(turma=turma_2, aluno=colega, criado_por=diretor)
    lancar_nota(turma=turma_1, disciplina=disciplina, aluno=aluno, valor=Decimal("8"), avaliacao="p1", ator=professor)
    lancar_nota(turma=turma_2, disciplina=disciplina, aluno=colega, valor=Decimal("9"), avaliacao="p1", ator=professor)

    notas_do_professor = consultar_notas(usuario=professor)

    assert set(notas_do_professor.values_list("aluno_id", flat=True)) == {aluno.id, colega.id}


def test_aluno_matriculado_com_professores_diferentes_tem_notas_de_ambos(
    instituicao, professor, outro_professor, diretor, aluno
):
    """Aluno pode ser 'filho' de varios professores (uma turma por professor)."""
    disciplina_1 = Disciplina.objects.create(instituicao=instituicao, nome="Matematica")
    disciplina_2 = Disciplina.objects.create(instituicao=instituicao, nome="Portugues")
    turma_do_professor = Turma.objects.create(
        instituicao=instituicao, nome="6o ano A", disciplina=disciplina_1, professor_responsavel=professor,
    )
    turma_do_outro_professor = Turma.objects.create(
        instituicao=instituicao, nome="6o ano A - Portugues", disciplina=disciplina_2,
        professor_responsavel=outro_professor,
    )
    matricular(turma=turma_do_professor, aluno=aluno, criado_por=diretor)
    matricular(turma=turma_do_outro_professor, aluno=aluno, criado_por=diretor)
    lancar_nota(turma=turma_do_professor, disciplina=disciplina_1, aluno=aluno, valor=Decimal("8"), avaliacao="p1", ator=professor)
    lancar_nota(turma=turma_do_outro_professor, disciplina=disciplina_2, aluno=aluno, valor=Decimal("6"), avaliacao="p1", ator=outro_professor)

    notas_do_aluno = consultar_notas(usuario=aluno)

    assert notas_do_aluno.count() == 2
    assert set(notas_do_aluno.values_list("turma_id", flat=True)) == {
        turma_do_professor.id, turma_do_outro_professor.id,
    }


def test_professor_nao_enxerga_nota_de_turma_de_outro_professor(
    instituicao, professor, outro_professor, diretor, aluno
):
    """Isolamento: professor so monitora as proprias turmas, nao a instituicao inteira."""
    turma_do_outro, disciplina = turma_com_disciplina(instituicao, outro_professor)
    matricular(turma=turma_do_outro, aluno=aluno, criado_por=diretor)
    lancar_nota(turma=turma_do_outro, disciplina=disciplina, aluno=aluno, valor=Decimal("8"), avaliacao="p1", ator=outro_professor)

    notas_do_professor = consultar_notas(usuario=professor)

    assert notas_do_professor.count() == 0
