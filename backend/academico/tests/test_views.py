from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from academico.matriculas import matricular
from academico.models import Disciplina, Turma
from academico.notas import lancar_nota

pytestmark = pytest.mark.django_db


def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


def turma(instituicao, professor):
    disciplina = Disciplina.objects.create(instituicao=instituicao, nome="Fisica")
    return Turma.objects.create(
        instituicao=instituicao,
        nome="Turma Fisica",
        disciplina=disciplina,
        professor_responsavel=professor,
    ), disciplina


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
