from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from academico.matriculas import matricular
from academico.models import Disciplina, Nota, Turma
from academico.notas import aprovar_nota, lancar_nota
from contas.auditoria import RegistroDeAuditoria


pytestmark = pytest.mark.django_db


def cliente_autenticado(usuario):
    cliente = APIClient()
    cliente.force_authenticate(usuario)
    return cliente


def cliente(usuario):
    return cliente_autenticado(usuario)


def turma(instituicao, professor):
    disciplina = Disciplina.objects.create(instituicao=instituicao, nome="Fisica")
    return Turma.objects.create(
        instituicao=instituicao,
        nome="Turma Fisica",
        disciplina=disciplina,
        professor_responsavel=professor,
    ), disciplina


def turma_com_disciplina(instituicao, professor):
    disciplina = Disciplina.objects.create(instituicao=instituicao, nome="Matematica")
    turma = Turma.objects.create(
        instituicao=instituicao,
        nome="9o ano A",
        disciplina=disciplina,
        professor_responsavel=professor,
    )
    return turma, disciplina


def criar_nota(instituicao, professor, diretor, aluno):
    turma, disciplina = turma_com_disciplina(instituicao, professor)
    matricular(turma=turma, aluno=aluno, criado_por=diretor)
    nota = lancar_nota(
        turma=turma,
        disciplina=disciplina,
        aluno=aluno,
        valor=Decimal("8"),
        avaliacao="p1",
        ator=professor,
    )
    return nota


def test_professor_lanca_nota_por_endpoint(instituicao, professor, diretor, aluno):
    turma_obj, disciplina = turma(instituicao, professor)
    matricular(turma=turma_obj, aluno=aluno, criado_por=diretor)

    resposta = cliente(professor).post(
        "/api/v1/academico/notas/",
        {
            "turma": turma_obj.id,
            "disciplina": disciplina.id,
            "aluno": aluno.id,
            "avaliacao": "p1",
            "valor": "8",
        },
        format="json",
    )

    assert resposta.status_code == 201
    assert resposta.json()["valor"] == "8.00"


def test_aluno_nao_ve_nota_de_colega_por_endpoint(instituicao, professor, diretor, aluno, colega):
    turma_obj, disciplina = turma(instituicao, professor)
    matricular(turma=turma_obj, aluno=colega, criado_por=diretor)
    nota = lancar_nota(
        turma=turma_obj,
        disciplina=disciplina,
        aluno=colega,
        valor=Decimal("7"),
        avaliacao="p1",
        ator=professor,
    )

    resposta = cliente(aluno).get(f"/api/v1/academico/notas/{nota.id}/")

    assert resposta.status_code == 403


def test_nota_de_outra_instituicao_responde_404(instituicao, professor, aluno, outra_instituicao):
    outro_professor = get_user_model().objects.create_user(
        email="professor-api-fora@teste.com",
        password="senha",
        instituicao=outra_instituicao,
        perfil="PROFESSOR",
    )
    outro_aluno = get_user_model().objects.create_user(
        email="aluno-api-fora@teste.com",
        password="senha",
        instituicao=outra_instituicao,
        perfil="ALUNO",
    )
    turma_obj, disciplina = turma(outra_instituicao, outro_professor)
    diretor_fora = get_user_model().objects.create_user(
        email="diretor-api-fora@teste.com",
        password="senha",
        instituicao=outra_instituicao,
        perfil="DIRETOR",
    )
    matricular(turma=turma_obj, aluno=outro_aluno, criado_por=diretor_fora)
    nota = lancar_nota(
        turma=turma_obj,
        disciplina=disciplina,
        aluno=outro_aluno,
        valor=Decimal("7"),
        avaliacao="p1",
        ator=outro_professor,
    )

    resposta = cliente(professor).get(f"/api/v1/academico/notas/{nota.id}/")

    assert resposta.status_code == 404


def test_diretor_nao_lanca_nota_nem_falta(instituicao, professor, diretor, aluno):
    nota = criar_nota(instituicao, professor, diretor, aluno)
    cliente = cliente_autenticado(diretor)

    resposta_nota = cliente.post(
        reverse("academico:notas"),
        {
            "turma": nota.turma_id,
            "disciplina": nota.disciplina_id,
            "aluno": aluno.id,
            "valor": "9",
            "avaliacao": "p2",
        },
        format="json",
    )
    resposta_falta = cliente.post(
        reverse("academico:faltas"),
        {"turma": nota.turma_id, "aluno": aluno.id, "data": "2026-08-05"},
        format="json",
    )

    assert resposta_nota.status_code == 403
    assert resposta_falta.status_code == 403


def test_superadmin_sem_perfil_nao_acessa_rotas_academicas(instituicao):
    superadmin = get_user_model().objects.create_superuser(
        email="superadmin-academico@teste.com", password="senha-segura-123"
    )
    cliente = cliente_autenticado(superadmin)

    assert cliente.get(reverse("academico:notas")).status_code == 403
    assert cliente.get(reverse("academico:turmas")).status_code == 403


def test_professor_aprova_nota_e_resposta_expoe_nota_oficial(
    instituicao, professor, diretor, aluno
):
    nota = criar_nota(instituicao, professor, diretor, aluno)
    cliente = cliente_autenticado(professor)

    resposta = cliente.post(
        reverse("academico:nota-aprovar", kwargs={"pk": nota.pk}),
        {"confirmacao": True, "motivo": "revisada pelo professor"},
        format="json",
    )

    assert resposta.status_code == 200
    assert resposta.data["oficial"] is True
    assert Nota.objects.get(pk=nota.pk).oficial is True
    assert RegistroDeAuditoria.objects.filter(
        objeto_tipo="Nota", objeto_id=str(nota.pk), acao="aprovar_nota"
    ).exists()


def test_aprovar_nota_sem_confirmacao_ou_motivo_retorna_400(
    instituicao, professor, diretor, aluno
):
    nota = criar_nota(instituicao, professor, diretor, aluno)
    cliente = cliente_autenticado(professor)

    resposta = cliente.post(
        reverse("academico:nota-aprovar", kwargs={"pk": nota.pk}),
        {"confirmacao": False, "motivo": "   "},
        format="json",
    )

    assert resposta.status_code == 400
    assert Nota.objects.get(pk=nota.pk).oficial is False


def test_professor_nao_aprova_nota_de_outra_instituicao(
    instituicao, outra_instituicao, professor, diretor, aluno
):
    professor_b = get_user_model().objects.create_user(
        email="professor-api-outra@teste.com", password="senha-segura-123",
        instituicao=outra_instituicao, perfil="PROFESSOR",
    )
    diretor_b = get_user_model().objects.create_user(
        email="diretor-api-outra@teste.com", password="senha-segura-123",
        instituicao=outra_instituicao, perfil="DIRETOR",
    )
    aluno_b = get_user_model().objects.create_user(
        email="aluno-api-outra@teste.com", password="senha-segura-123",
        instituicao=outra_instituicao, perfil="ALUNO",
    )
    nota = criar_nota(outra_instituicao, professor_b, diretor_b, aluno_b)
    aprovar_nota(nota=nota, ator=professor_b, confirmacao=True, motivo="revisao legitima")

    resposta = cliente_autenticado(professor).post(
        reverse("academico:nota-aprovar", kwargs={"pk": nota.pk}),
        {"confirmacao": True, "motivo": "tentativa cross-tenant"},
        format="json",
    )

    assert resposta.status_code == 404
    assert Nota.objects.get(pk=nota.pk).oficial is True
