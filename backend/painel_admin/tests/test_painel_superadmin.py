import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from contas.auditoria import RegistroDeAuditoria
from contas.models import Instituicao, Perfil


pytestmark = pytest.mark.django_db


def criar_contas():
    escola = Instituicao.objects.create(nome="Escola", documento="00.000.000/0001-80")
    superadmin = get_user_model().objects.create_superuser(
        email="admin@prisma.test", password="senha-segura-123"
    )
    aluno = get_user_model().objects.create_user(
        email="aluno@escola.test", password="senha-segura-123",
        first_name="Ana", instituicao=escola, perfil=Perfil.ALUNO,
    )
    return superadmin, aluno


def test_painel_exige_superadmin():
    _, aluno = criar_contas()
    cliente = Client()
    cliente.force_login(aluno)

    resposta = cliente.get(reverse("painel-dashboard"))

    assert resposta.status_code == 403


def test_superadmin_ve_usuario():
    superadmin, aluno = criar_contas()
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.get(reverse("painel-usuario", kwargs={"pk": aluno.pk}))

    assert resposta.status_code == 200
    assert aluno.email.encode() in resposta.content


def test_superadmin_troca_perfil_com_motivo_e_auditoria():
    superadmin, aluno = criar_contas()
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(
        reverse("painel-usuario-perfil", kwargs={"pk": aluno.pk}),
        {"perfil": Perfil.PROFESSOR, "motivo": "mudanca de funcao"},
    )

    assert resposta.status_code == 302
    aluno.refresh_from_db()
    assert aluno.perfil == Perfil.PROFESSOR
    registro = RegistroDeAuditoria.objects.get(objeto_id=str(aluno.pk), acao="alterar_perfil")
    assert "ALUNO -> PROFESSOR" in registro.motivo
    assert "mudanca de funcao" in registro.motivo


def test_troca_de_perfil_sem_motivo_nao_altera_usuario():
    superadmin, aluno = criar_contas()
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(
        reverse("painel-usuario-perfil", kwargs={"pk": aluno.pk}),
        {"perfil": Perfil.PROFESSOR},
    )

    assert resposta.status_code == 400
    aluno.refresh_from_db()
    assert aluno.perfil == Perfil.ALUNO
