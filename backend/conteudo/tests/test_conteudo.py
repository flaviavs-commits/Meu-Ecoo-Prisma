import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from academico.matriculas import matricular
from conteudo.excecoes import ConteudoEstadoError
from conteudo.models import Material, OrigemConteudo, Prova, StatusConteudo
from conteudo.servico import adicionar_questao, criar_material, criar_prova, oficializar_prova
from contas.auditoria import RegistroDeAuditoria

pytestmark = pytest.mark.django_db


def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


def prova_rascunho(turma, disciplina, autor, origem=OrigemConteudo.MANUAL):
    return criar_prova(
        instituicao=turma.instituicao,
        turma=turma,
        disciplina=disciplina,
        autor=autor,
        titulo="Prova de Portugues",
        origem=origem,
    )


def test_conteudo_de_ia_nasce_rascunho(turma_disciplina, professor):
    turma, disciplina = turma_disciplina

    prova = prova_rascunho(turma, disciplina, professor, OrigemConteudo.IA)

    assert prova.status == StatusConteudo.RASCUNHO


def test_nao_existe_caminho_de_criacao_oficial_direta(turma_disciplina, professor):
    turma, disciplina = turma_disciplina

    with pytest.raises(ConteudoEstadoError):
        Prova.objects.create(
            instituicao=turma.instituicao,
            turma=turma,
            disciplina=disciplina,
            autor=professor,
            titulo="Nao pode",
            origem=OrigemConteudo.MANUAL,
            status=StatusConteudo.OFICIAL,
        )


def test_oficializar_sem_confirmacao_retorna_400(turma_disciplina, professor):
    turma, disciplina = turma_disciplina
    prova = prova_rascunho(turma, disciplina, professor)
    adicionar_questao(prova=prova, enunciado="Questao", gabarito="A")

    resposta = cliente(professor).post(
        f"/api/v1/conteudo/provas/{prova.id}/oficializar/", {"motivo": "revisei"}, format="json"
    )

    assert resposta.status_code == 400


def test_oficializar_sem_motivo_retorna_400(turma_disciplina, professor):
    turma, disciplina = turma_disciplina
    prova = prova_rascunho(turma, disciplina, professor)
    adicionar_questao(prova=prova, enunciado="Questao", gabarito="A")

    resposta = cliente(professor).post(
        f"/api/v1/conteudo/provas/{prova.id}/oficializar/", {"confirmacao": True}, format="json"
    )

    assert resposta.status_code == 400


def test_oficializar_sem_questao_retorna_422(turma_disciplina, professor):
    turma, disciplina = turma_disciplina
    prova = prova_rascunho(turma, disciplina, professor)

    resposta = cliente(professor).post(
        f"/api/v1/conteudo/provas/{prova.id}/oficializar/",
        {"confirmacao": True, "motivo": "revisei"},
        format="json",
    )

    assert resposta.status_code == 422


def test_prova_ja_oficial_retorna_409(turma_disciplina, professor):
    turma, disciplina = turma_disciplina
    prova = prova_rascunho(turma, disciplina, professor)
    adicionar_questao(prova=prova, enunciado="Questao", gabarito="A")
    oficializar_prova(prova=prova, ator=professor, confirmacao=True, motivo="primeira revisao")

    resposta = cliente(professor).post(
        f"/api/v1/conteudo/provas/{prova.id}/oficializar/",
        {"confirmacao": True, "motivo": "segunda revisao"},
        format="json",
    )

    assert resposta.status_code == 409


def test_oficializacao_grava_revisao_e_auditoria(turma_disciplina, professor):
    turma, disciplina = turma_disciplina
    prova = prova_rascunho(turma, disciplina, professor)
    adicionar_questao(prova=prova, enunciado="Questao", gabarito="A")

    oficializar_prova(prova=prova, ator=professor, confirmacao=True, motivo="revisei tudo")
    prova.refresh_from_db()

    assert prova.status == StatusConteudo.OFICIAL
    assert prova.revisado_por_id == professor.id
    assert RegistroDeAuditoria.objects.filter(
        objeto_tipo="Prova", objeto_id=str(prova.id), acao="oficializar_prova"
    ).exists()


def test_professor_que_nao_e_autor_nao_oficializa(turma_disciplina, professor, outro_professor):
    turma, disciplina = turma_disciplina
    prova = prova_rascunho(turma, disciplina, professor)
    adicionar_questao(prova=prova, enunciado="Questao", gabarito="A")

    resposta = cliente(outro_professor).post(
        f"/api/v1/conteudo/provas/{prova.id}/oficializar/",
        {"confirmacao": True, "motivo": "nao sou autor"},
        format="json",
    )

    assert resposta.status_code == 403


def test_aluno_nao_ve_prova_em_rascunho(turma_disciplina, professor, aluno):
    turma, disciplina = turma_disciplina
    prova = prova_rascunho(turma, disciplina, professor)

    resposta = cliente(aluno).get(f"/api/v1/conteudo/provas/{prova.id}/")

    assert resposta.status_code == 404


def test_json_do_aluno_nao_contem_gabarito(turma_disciplina, professor, diretor, aluno):
    turma, disciplina = turma_disciplina
    matricular(turma=turma, aluno=aluno, criado_por=diretor)
    prova = prova_rascunho(turma, disciplina, professor)
    adicionar_questao(prova=prova, enunciado="Quanto e 1+1?", gabarito="2")
    oficializar_prova(prova=prova, ator=professor, confirmacao=True, motivo="revisada")

    resposta = cliente(aluno).get(f"/api/v1/conteudo/provas/{prova.id}/")

    assert resposta.status_code == 200
    assert "gabarito" not in resposta.json()["questoes"][0]


def test_material_de_outra_instituicao_responde_404(turma_disciplina, professor, outra_instituicao):
    turma, disciplina = turma_disciplina
    autor_externo = get_user_model().objects.create_user(
        email="autor-material-fora@teste.com",
        password="senha",
        instituicao=outra_instituicao,
        perfil="PROFESSOR",
    )
    material = criar_material(
        instituicao=outra_instituicao,
        turma=None,
        disciplina=None,
        autor=autor_externo,
        titulo="Material externo",
        origem=OrigemConteudo.MANUAL,
    )

    resposta = cliente(professor).get(f"/api/v1/conteudo/materiais/{material.id}/")

    assert resposta.status_code == 404
