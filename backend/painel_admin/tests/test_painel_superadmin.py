from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from contas.auditoria import RegistroDeAuditoria
from contas.models import Instituicao, Perfil
from creditos.models import Lancamento, TipoLancamento
from creditos.saldo import saldo_usuario


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


def test_superadmin_cria_instituicao_com_credito_e_auditoria():
    superadmin, _ = criar_contas()
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(
        reverse("painel-instituicoes"),
        {
            "nome": "Instituto Prisma",
            "documento": "00.000.000/0001-81",
            "creditos_iniciais": "250.5000",
        },
    )

    assert resposta.status_code == 302
    instituicao = Instituicao.objects.get(documento="00.000.000/0001-81")
    lancamento = Lancamento.objects.get(instituicao=instituicao)
    assert lancamento.tipo == TipoLancamento.CREDITO
    assert lancamento.quantidade == Decimal("250.5000")
    assert lancamento.criado_por == superadmin
    assert RegistroDeAuditoria.objects.filter(
        ator=superadmin,
        acao="criar_instituicao",
        objeto_tipo="Instituicao",
        objeto_id=str(instituicao.pk),
    ).exists()


def test_criacao_de_instituicao_duplicada_nao_cria_novo_ledger():
    superadmin, _ = criar_contas()
    Instituicao.objects.create(nome="Existente", documento="00.000.000/0001-82")
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(
        reverse("painel-instituicoes"),
        {
            "nome": "Duplicada",
            "documento": "00.000.000/0001-82",
            "creditos_iniciais": "50",
        },
    )

    assert resposta.status_code == 200
    assert Instituicao.objects.filter(documento="00.000.000/0001-82").count() == 1
    assert Lancamento.objects.filter(quantidade=Decimal("50")).exists() is False


def test_diretor_nao_cria_instituicao_nem_conta_de_teste():
    _, aluno = criar_contas()
    cliente = Client()
    cliente.force_login(aluno)

    assert cliente.post(reverse("painel-instituicoes"), {}).status_code == 403
    assert cliente.post(reverse("painel-contas-teste"), {}).status_code == 403


def test_superadmin_cria_conta_de_teste_academica_sem_privilegios():
    superadmin, aluno = criar_contas()
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(
        reverse("painel-contas-teste"),
        {
            "email": "professor.teste@escola.test",
            "first_name": "Professor",
            "last_name": "Teste",
            "instituicao": aluno.instituicao.pk,
            "perfil": Perfil.PROFESSOR,
            "password1": "Senha-de-teste-12345",
            "password2": "Senha-de-teste-12345",
        },
    )

    assert resposta.status_code == 302
    conta = get_user_model().objects.get(email="professor.teste@escola.test")
    assert conta.check_password("Senha-de-teste-12345") is True
    assert conta.first_name == "Professor"
    assert conta.instituicao == aluno.instituicao
    assert conta.perfil == Perfil.PROFESSOR
    assert conta.ativo is True
    assert conta.is_active is True
    assert conta.is_staff is False
    assert conta.is_superuser is False
    assert RegistroDeAuditoria.objects.filter(
        ator=superadmin,
        acao="criar_conta_teste",
        objeto_tipo="Usuario",
        objeto_id=str(conta.pk),
    ).exists()


def test_conta_de_teste_com_senha_fraca_faz_rollback():
    superadmin, aluno = criar_contas()
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(
        reverse("painel-contas-teste"),
        {
            "email": "aluno.teste@escola.test",
            "first_name": "Aluno",
            "last_name": "Teste",
            "instituicao": aluno.instituicao.pk,
            "perfil": Perfil.ALUNO,
            "password1": "123",
            "password2": "123",
        },
    )

    assert resposta.status_code == 200
    assert get_user_model().objects.filter(email="aluno.teste@escola.test").exists() is False


def test_visitante_sem_login_e_redirecionado_para_login_do_admin_e_nao_404():
    cliente = Client()

    resposta = cliente.get(reverse("painel-dashboard"))

    assert resposta.status_code == 302
    assert resposta.url.startswith(reverse("admin:login"))

    resposta_login = cliente.get(resposta.url)
    assert resposta_login.status_code == 200


def test_staff_nao_superadmin_nao_acessa_painel():
    escola = Instituicao.objects.create(nome="Escola staff", documento="00.000.000/0001-71")
    staff = get_user_model().objects.create_user(
        email="staff@escola.test", password="senha-segura-123",
        first_name="Bea", instituicao=escola, perfil=Perfil.PROFESSOR,
        is_staff=True,
    )
    cliente = Client()
    cliente.force_login(staff)

    resposta = cliente.get(reverse("painel-dashboard"))

    assert resposta.status_code == 403


def test_diretor_nao_acessa_painel():
    escola = Instituicao.objects.create(nome="Escola diretor", documento="00.000.000/0001-72")
    diretor = get_user_model().objects.create_user(
        email="diretor-painel@escola.test", password="senha-segura-123",
        instituicao=escola, perfil=Perfil.DIRETOR,
    )
    cliente = Client()
    cliente.force_login(diretor)

    assert cliente.get(reverse("painel-dashboard")).status_code == 403


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


def test_troca_para_perfil_invalido_retorna_bad_request():
    superadmin, aluno = criar_contas()
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(
        reverse("painel-usuario-perfil", kwargs={"pk": aluno.pk}),
        {"perfil": "SUPERADMIN", "motivo": "tentativa invalida"},
    )

    assert resposta.status_code == 400
    aluno.refresh_from_db()
    assert aluno.perfil == Perfil.ALUNO


def test_registros_lista_auditoria_paginada_e_filtra_por_acao():
    superadmin, aluno = criar_contas()
    cliente = Client()
    cliente.force_login(superadmin)
    for indice in range(3):
        RegistroDeAuditoria.objects.create(
            ator=superadmin, acao="alterar_perfil", objeto_tipo="Usuario",
            objeto_id=str(aluno.pk), motivo=f"motivo {indice}",
        )
    RegistroDeAuditoria.objects.create(
        ator=superadmin, acao="desativar_usuario", objeto_tipo="Usuario",
        objeto_id=str(aluno.pk), motivo="desligamento",
    )

    resposta = cliente.get(reverse("painel-registros"), {"acao": "alterar_perfil"})

    assert resposta.status_code == 200
    assert resposta.content.count(b"<td>alterar_perfil</td>") == 3
    assert b"<td>desativar_usuario</td>" not in resposta.content


def test_registros_exige_superadmin():
    _, aluno = criar_contas()
    cliente = Client()
    cliente.force_login(aluno)

    resposta = cliente.get(reverse("painel-registros"))

    assert resposta.status_code == 403


def test_desativar_usuario_exige_confirmacao_e_motivo():
    superadmin, aluno = criar_contas()
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(reverse("painel-usuario-desativar", kwargs={"pk": aluno.pk}), {})

    assert resposta.status_code == 400
    aluno.refresh_from_db()
    assert aluno.ativo is True


def test_desativar_usuario_com_confirmacao_desativa_e_audita():
    superadmin, aluno = criar_contas()
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(
        reverse("painel-usuario-desativar", kwargs={"pk": aluno.pk}),
        {"confirmacao": "on", "motivo": "encerramento de matricula"},
    )

    assert resposta.status_code == 302
    aluno.refresh_from_db()
    assert aluno.ativo is False
    assert aluno.is_active is False
    assert RegistroDeAuditoria.objects.filter(
        objeto_id=str(aluno.pk), acao="desativar_usuario"
    ).exists()


def test_zerar_creditos_exige_confirmacao_e_motivo():
    superadmin, aluno = criar_contas()
    Lancamento.objects.create(
        instituicao=aluno.instituicao, usuario=aluno, tipo=TipoLancamento.ALOCACAO,
        quantidade=Decimal("10"), motivo="carga inicial", criado_por=superadmin,
    )
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(reverse("painel-usuario-zerar-creditos", kwargs={"pk": aluno.pk}), {})

    assert resposta.status_code == 400
    assert saldo_usuario(aluno.pk) == Decimal("10")


def test_zerar_creditos_com_confirmacao_zera_saldo_e_audita():
    superadmin, aluno = criar_contas()
    Lancamento.objects.create(
        instituicao=aluno.instituicao, usuario=aluno, tipo=TipoLancamento.ALOCACAO,
        quantidade=Decimal("10"), motivo="carga inicial", criado_por=superadmin,
    )
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(
        reverse("painel-usuario-zerar-creditos", kwargs={"pk": aluno.pk}),
        {"confirmacao": "on", "motivo": "encerramento de matricula"},
    )

    assert resposta.status_code == 302
    assert saldo_usuario(aluno.pk) == Decimal("0")
    assert RegistroDeAuditoria.objects.filter(
        objeto_id=str(aluno.pk), acao="reduzir_alocacao"
    ).exists()


def test_zerar_creditos_com_saldo_zero_nao_gera_lancamento():
    superadmin, aluno = criar_contas()
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(
        reverse("painel-usuario-zerar-creditos", kwargs={"pk": aluno.pk}),
        {"confirmacao": "on", "motivo": "sem saldo"},
    )

    assert resposta.status_code == 400
    assert saldo_usuario(aluno.pk) == Decimal("0")


def test_zerar_creditos_rejeita_motivo_so_com_espacos():
    superadmin, aluno = criar_contas()
    Lancamento.objects.create(
        instituicao=aluno.instituicao, usuario=aluno, tipo=TipoLancamento.ALOCACAO,
        quantidade=Decimal("10"), motivo="carga inicial", criado_por=superadmin,
    )
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(
        reverse("painel-usuario-zerar-creditos", kwargs={"pk": aluno.pk}),
        {"confirmacao": "on", "motivo": "   "},
    )

    assert resposta.status_code == 400
    assert saldo_usuario(aluno.pk) == Decimal("10")
