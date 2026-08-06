"""O professor envia avisos; quem lê é quem está matriculado na turma."""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from academico.matriculas import matricular
from academico.models import Disciplina, Turma
from avisos.excecoes import AvisoPermissaoError
from avisos.servico import avisos_visiveis, enviar_aviso
from contas.models import Instituicao, Perfil

pytestmark = pytest.mark.django_db


@pytest.fixture
def turma(instituicao, professor):
    disciplina = Disciplina.objects.create(instituicao=instituicao, nome="Biologia")
    turma = Turma.objects.create(
        instituicao=instituicao,
        nome="3o ano",
        disciplina=disciplina,
        professor_responsavel=professor,
    )
    turma.professores.add(professor)
    return turma


def test_professor_envia_aviso_para_a_propria_turma(turma, professor):
    aviso = enviar_aviso(
        turma=turma, autor=professor, titulo="Prova na sexta", mensagem="Estudem os capitulos 1 a 3."
    )

    assert aviso.instituicao_id == turma.instituicao_id
    assert aviso.autor == professor


def test_professor_de_outra_turma_nao_envia(turma, instituicao):
    forasteiro = get_user_model().objects.create_user(
        "outro@escola.test", "senha", instituicao=instituicao, perfil=Perfil.PROFESSOR
    )

    with pytest.raises(AvisoPermissaoError):
        enviar_aviso(turma=turma, autor=forasteiro, titulo="Oi", mensagem="Texto")


def test_aluno_nao_envia_aviso(turma, aluno, diretor):
    matricular(turma=turma, aluno=aluno, criado_por=diretor)

    with pytest.raises(AvisoPermissaoError):
        enviar_aviso(turma=turma, autor=aluno, titulo="Oi", mensagem="Texto")


def test_diretor_envia_para_qualquer_turma_da_instituicao(turma, diretor):
    aviso = enviar_aviso(turma=turma, autor=diretor, titulo="Reuniao", mensagem="Sexta as 19h.")

    assert aviso.autor == diretor


def test_aviso_exige_titulo_e_mensagem(turma, professor):
    with pytest.raises(ValueError):
        enviar_aviso(turma=turma, autor=professor, titulo="   ", mensagem="Texto")


def test_aluno_matriculado_le_o_aviso_da_sua_turma(turma, professor, aluno, diretor):
    matricular(turma=turma, aluno=aluno, criado_por=diretor)
    enviar_aviso(turma=turma, autor=professor, titulo="Prova", mensagem="Sexta")

    assert avisos_visiveis(aluno).count() == 1


def test_aluno_de_outra_turma_nao_le(turma, professor, instituicao):
    enviar_aviso(turma=turma, autor=professor, titulo="Prova", mensagem="Sexta")
    de_fora = get_user_model().objects.create_user(
        "defora@escola.test", "senha", instituicao=instituicao, perfil=Perfil.ALUNO
    )

    assert avisos_visiveis(de_fora).count() == 0


def test_aviso_nao_atravessa_instituicao(turma, professor):
    enviar_aviso(turma=turma, autor=professor, titulo="Prova", mensagem="Sexta")
    outra = Instituicao.objects.create(nome="Escola Rival", documento="22.222.222/0001-22")
    intruso = get_user_model().objects.create_user(
        "intruso@rival.test", "senha", instituicao=outra, perfil=Perfil.DIRETOR
    )

    assert avisos_visiveis(intruso).count() == 0


def api_de(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


def test_api_envia_e_lista_aviso(turma, professor, aluno, diretor):
    matricular(turma=turma, aluno=aluno, criado_por=diretor)
    url = reverse("avisos:avisos")

    resposta = api_de(professor).post(
        url, {"turma": turma.id, "titulo": "Trabalho", "mensagem": "Entrega na terca"},
        format="json",
    )
    assert resposta.status_code == 201

    listagem = api_de(aluno).get(url)
    assert listagem.status_code == 200
    assert listagem.json()["results"][0]["titulo"] == "Trabalho"


def test_api_recusa_turma_de_outra_instituicao(turma, professor):
    outra = Instituicao.objects.create(nome="Escola Rival", documento="33.333.333/0001-33")
    intruso = get_user_model().objects.create_user(
        "prof@rival.test", "senha", instituicao=outra, perfil=Perfil.PROFESSOR
    )
    resposta = api_de(intruso).post(
        reverse("avisos:avisos"),
        {"turma": turma.id, "titulo": "Oi", "mensagem": "Texto"},
        format="json",
    )

    assert resposta.status_code == 404
