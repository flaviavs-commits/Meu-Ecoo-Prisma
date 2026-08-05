from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from academico.matriculas import matricular
from academico.models import Disciplina, Turma
from academico.notas import (
    AcademicoConfirmacaoError,
    AcademicoPermissaoError,
    NotaJaOficialError,
    aprovar_nota,
    consultar_notas,
    lancar_nota,
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


def test_diretor_filtra_aluno_alvo(instituicao, professor, outro_professor, diretor, aluno, colega):
    turma_a, disciplina = turma_com_disciplina(instituicao, professor)
    turma_b = Turma.objects.create(
        instituicao=instituicao, nome="9o ano B", disciplina=disciplina,
        professor_responsavel=outro_professor,
    )
    matricular(turma=turma_a, aluno=aluno, criado_por=diretor)
    matricular(turma=turma_b, aluno=colega, criado_por=diretor)
    nota_a = lancar_nota(
        turma=turma_a, disciplina=disciplina, aluno=aluno,
        valor=Decimal("8"), avaliacao="p1", ator=professor,
    )
    nota_b = lancar_nota(
        turma=turma_b, disciplina=disciplina, aluno=colega,
        valor=Decimal("9"), avaliacao="p1", ator=outro_professor,
    )
    aprovar_nota(nota=nota_a, ator=professor, confirmacao=True, motivo="revisao A")
    aprovar_nota(nota=nota_b, ator=outro_professor, confirmacao=True, motivo="revisao B")

    assert list(consultar_notas(usuario=diretor, aluno_alvo=aluno).values_list("id", flat=True)) == [nota_a.id]


def test_diretor_de_outra_instituicao_nao_enxerga_nota_aprovada(
    outra_instituicao, diretor
):
    professor_b = get_user_model().objects.create_user(
        email="professor-outra-instituicao@teste.com", password="senha-segura-123",
        instituicao=outra_instituicao, perfil="PROFESSOR",
    )
    diretor_b = get_user_model().objects.create_user(
        email="diretor-outra-instituicao@teste.com", password="senha-segura-123",
        instituicao=outra_instituicao, perfil="DIRETOR",
    )
    aluno_b = get_user_model().objects.create_user(
        email="aluno-outra-instituicao@teste.com", password="senha-segura-123",
        instituicao=outra_instituicao, perfil="ALUNO",
    )
    turma_b, disciplina_b = turma_com_disciplina(outra_instituicao, professor_b)
    matricular(turma=turma_b, aluno=aluno_b, criado_por=diretor_b)
    nota_b = lancar_nota(
        turma=turma_b, disciplina=disciplina_b, aluno=aluno_b,
        valor=Decimal("9"), avaliacao="p1", ator=professor_b,
    )
    aprovar_nota(nota=nota_b, ator=professor_b, confirmacao=True, motivo="revisao")

    assert not consultar_notas(usuario=diretor).filter(pk=nota_b.pk).exists()


def test_aprovar_nota_marca_oficial_e_audita(instituicao, professor, diretor, aluno):
    turma, disciplina = turma_com_disciplina(instituicao, professor)
    matricular(turma=turma, aluno=aluno, criado_por=diretor)
    nota = lancar_nota(
        turma=turma, disciplina=disciplina, aluno=aluno,
        valor=Decimal("8"), avaliacao="p1", ator=professor,
    )

    aprovar_nota(nota=nota, ator=professor, confirmacao=True, motivo="revisada pelo professor")

    nota.refresh_from_db()
    assert nota.oficial is True
    assert RegistroDeAuditoria.objects.filter(
        objeto_tipo="Nota", objeto_id=str(nota.id), acao="aprovar_nota",
        motivo="revisada pelo professor",
    ).exists()
    with pytest.raises(NotaJaOficialError):
        aprovar_nota(nota=nota, ator=professor, confirmacao=True, motivo="segunda revisao")


def test_aprovar_nota_exige_confirmacao_e_motivo(instituicao, professor, diretor, aluno):
    turma, disciplina = turma_com_disciplina(instituicao, professor)
    matricular(turma=turma, aluno=aluno, criado_por=diretor)
    nota = lancar_nota(
        turma=turma, disciplina=disciplina, aluno=aluno,
        valor=Decimal("8"), avaliacao="p1", ator=professor,
    )

    with pytest.raises(AcademicoConfirmacaoError):
        aprovar_nota(nota=nota, ator=professor, confirmacao=False, motivo="revisao")
    with pytest.raises(AcademicoConfirmacaoError):
        aprovar_nota(nota=nota, ator=professor, confirmacao=True, motivo="   ")
    nota.refresh_from_db()
    assert nota.oficial is False


def test_professor_nao_aprova_nota_de_turma_de_outro_professor(
    instituicao, professor, outro_professor, diretor, aluno
):
    turma, disciplina = turma_com_disciplina(instituicao, outro_professor)
    matricular(turma=turma, aluno=aluno, criado_por=diretor)
    nota = lancar_nota(
        turma=turma, disciplina=disciplina, aluno=aluno,
        valor=Decimal("8"), avaliacao="p1", ator=outro_professor,
    )

    with pytest.raises(AcademicoPermissaoError):
        aprovar_nota(nota=nota, ator=professor, confirmacao=True, motivo="tentativa")
    nota.refresh_from_db()
    assert nota.oficial is False


def test_aluno_e_professor_enxergam_nota_em_rascunho(
    instituicao, professor, diretor, aluno
):
    turma, disciplina = turma_com_disciplina(instituicao, professor)
    matricular(turma=turma, aluno=aluno, criado_por=diretor)
    nota = lancar_nota(
        turma=turma, disciplina=disciplina, aluno=aluno,
        valor=Decimal("8"), avaliacao="p1", ator=professor,
    )

    assert nota.oficial is False
    assert consultar_notas(usuario=aluno).filter(pk=nota.pk).exists()
    assert consultar_notas(usuario=professor).filter(pk=nota.pk).exists()


def test_diretor_nao_enxerga_nota_em_rascunho(instituicao, professor, diretor, aluno):
    turma, disciplina = turma_com_disciplina(instituicao, professor)
    matricular(turma=turma, aluno=aluno, criado_por=diretor)
    nota = lancar_nota(
        turma=turma, disciplina=disciplina, aluno=aluno,
        valor=Decimal("8"), avaliacao="p1", ator=professor,
    )

    assert not consultar_notas(usuario=diretor).filter(pk=nota.pk).exists()


def test_usuario_sem_instituicao_nao_consulta_notas(db):
    usuario = get_user_model().objects.create_user(
        email="sem-instituicao@teste.com", password="senha-segura-123", perfil="DIRETOR",
    )

    with pytest.raises(AcademicoPermissaoError) as erro:
        consultar_notas(usuario=usuario)

    assert erro.value.codigo == "sem_instituicao"
