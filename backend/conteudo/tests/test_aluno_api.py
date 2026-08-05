from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from academico.models import Disciplina
from conteudo.models import FormatoMaterial, Material, OrigemConteudo, StatusConteudo
from conteudo.servico import criar_material
from contas.models import Instituicao, Perfil
from django.contrib.auth import get_user_model
from limites.models import AssinaturaInstituicao, PlanoInstitucional

pytestmark = pytest.mark.django_db


def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


@pytest.fixture
def instituicao(db):
    return Instituicao.objects.create(
        nome="Escola Conteudo Aluno", documento="00.000.000/0001-51"
    )


@pytest.fixture
def outra_instituicao(db):
    return Instituicao.objects.create(
        nome="Outra Escola Conteudo", documento="00.000.000/0001-52"
    )


@pytest.fixture
def aluno(db, instituicao):
    return get_user_model().objects.create_user(
        email="aluno-conteudo-api@teste.com",
        password="senha-segura-123",
        instituicao=instituicao,
        perfil=Perfil.ALUNO,
    )


@pytest.fixture
def outro_aluno(db, outra_instituicao):
    return get_user_model().objects.create_user(
        email="outro-aluno-conteudo-api@teste.com",
        password="senha-segura-123",
        instituicao=outra_instituicao,
        perfil=Perfil.ALUNO,
    )


def disciplina(instituicao):
    return Disciplina.objects.create(instituicao=instituicao, nome="Matematica")


def test_aluno_lista_materiais_da_propria_instituicao(aluno, outro_aluno):
    propria = criar_material(
        instituicao=aluno.instituicao,
        turma=None,
        disciplina=disciplina(aluno.instituicao),
        autor=aluno,
        titulo="Resumo proprio",
        origem=OrigemConteudo.MANUAL,
    )
    externa = criar_material(
        instituicao=outro_aluno.instituicao,
        turma=None,
        disciplina=disciplina(outro_aluno.instituicao),
        autor=outro_aluno,
        titulo="Resumo externo",
        origem=OrigemConteudo.MANUAL,
    )

    resposta = cliente(aluno).get("/api/v1/conteudo/materiais/")

    assert resposta.status_code == 200
    ids = [item["id"] for item in resposta.data["results"]]
    assert propria.id in ids
    assert externa.id not in ids


def test_aluno_gera_material_e_debita_percentual(aluno):
    resposta = cliente(aluno).post(
        "/api/v1/conteudo/materiais/gerar/",
        {
            "titulo": "Resumo de funções",
            "disciplina": "Matematica",
            "formato": "RESUMO",
            "conteudo": "Funções do segundo grau",
        },
        format="json",
    )

    assert resposta.status_code == 201
    material = Material.objects.get(pk=resposta.data["id"])
    assert material.origem == OrigemConteudo.IA
    assert material.formato == FormatoMaterial.RESUMO
    assert aluno.consumos_ia.count() == 1


def test_aluno_nao_abre_rascunho_de_outro_aluno(aluno, outro_aluno):
    material = criar_material(
        instituicao=outro_aluno.instituicao,
        turma=None,
        disciplina=None,
        autor=outro_aluno,
        titulo="Privado",
        origem=OrigemConteudo.IA,
    )

    resposta = cliente(aluno).get(f"/api/v1/conteudo/materiais/{material.id}/")

    assert resposta.status_code == 404


def test_material_gerado_e_bloqueado_sem_percentual_disponivel(aluno):
    plano = PlanoInstitucional.objects.get(codigo="PRISMA")
    plano.limite_percentual_por_conta = Decimal("0")
    plano.save(update_fields=["limite_percentual_por_conta"])
    AssinaturaInstituicao.objects.create(instituicao=aluno.instituicao, plano=plano)

    resposta = cliente(aluno).post(
        "/api/v1/conteudo/materiais/gerar/",
        {
            "titulo": "Resumo bloqueado",
            "disciplina": "Matematica",
            "formato": "RESUMO",
            "conteudo": "conteudo",
        },
        format="json",
    )

    assert resposta.status_code == 422
