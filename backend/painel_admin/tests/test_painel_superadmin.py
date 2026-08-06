from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from contas.auditoria import RegistroDeAuditoria
from contas.models import Instituicao, Perfil, TipoInstituicao
from creditos.models import Lancamento, TipoLancamento
from creditos.saldo import saldo_usuario
from limites.models import AssinaturaInstituicao, PlanoInstitucional


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


def test_superadmin_cria_instituicao_com_plano_e_auditoria():
    superadmin, _ = criar_contas()
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(
        reverse("painel-instituicoes"),
        {
            "nome": "Instituto Prisma",
            "documento": "00.000.000/0001-81",
            "plano": PlanoInstitucional.objects.get(codigo="PRISMA_PRO").pk,
        },
    )

    assert resposta.status_code == 302
    instituicao = Instituicao.objects.get(documento="00.000.000/0001-81")
    assinatura = AssinaturaInstituicao.objects.get(instituicao=instituicao)
    assert assinatura.plano.codigo == "PRISMA_PRO"
    assert RegistroDeAuditoria.objects.filter(
        ator=superadmin,
        acao="criar_instituicao",
        objeto_tipo="Instituicao",
        objeto_id=str(instituicao.pk),
    ).exists()


def test_superadmin_e_vinculado_a_vitis_souls_sem_documento():
    superadmin, _ = criar_contas()

    superadmin.refresh_from_db()
    assert superadmin.eh_provider is True
    assert superadmin.perfil == Perfil.PROVIDER
    assert superadmin.instituicao.codigo == "VITIS_SOULS"
    assert superadmin.instituicao.tipo == TipoInstituicao.PROVEDORA
    assert superadmin.instituicao.documento is None


def test_criacao_de_instituicao_duplicada_nao_cria_nova_escola():
    superadmin, _ = criar_contas()
    Instituicao.objects.create(nome="Existente", documento="00.000.000/0001-82")
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(
        reverse("painel-instituicoes"),
        {
            "nome": "Duplicada",
            "documento": "00.000.000/0001-82",
            "plano": PlanoInstitucional.objects.get(codigo="PRISMA").pk,
        },
    )

    assert resposta.status_code == 200
    assert Instituicao.objects.filter(documento="00.000.000/0001-82").count() == 1
    assert AssinaturaInstituicao.objects.filter(instituicao__documento="00.000.000/0001-82").count() == 0


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


def test_conta_de_teste_nao_pode_usar_tier_provider():
    superadmin, aluno = criar_contas()
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(
        reverse("painel-contas-teste"),
        {
            "email": "provider.teste@escola.test",
            "first_name": "Provider",
            "last_name": "Invalido",
            "instituicao": aluno.instituicao.pk,
            "perfil": Perfil.PROVIDER,
            "password1": "Senha-de-teste-12345",
            "password2": "Senha-de-teste-12345",
        },
    )

    assert resposta.status_code == 200
    assert get_user_model().objects.filter(email="provider.teste@escola.test").exists() is False


def test_conta_de_teste_nao_pode_ser_criada_na_vitis_souls():
    superadmin, _ = criar_contas()
    vitis = superadmin.instituicao
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(
        reverse("painel-contas-teste"),
        {
            "email": "academico@vitis.test",
            "first_name": "Conta",
            "last_name": "Inválida",
            "instituicao": vitis.pk,
            "perfil": Perfil.ALUNO,
            "password1": "Senha-de-teste-12345",
            "password2": "Senha-de-teste-12345",
        },
    )

    assert resposta.status_code == 200
    assert get_user_model().objects.filter(email="academico@vitis.test").exists() is False


def test_provider_inativo_nao_acessa_painel():
    superadmin, _ = criar_contas()
    superadmin.ativo = False
    superadmin.save(update_fields=["ativo", "atualizado_em"])
    cliente = Client()
    cliente.force_login(superadmin)

    assert cliente.get(reverse("painel-dashboard")).status_code == 403


def test_superadmin_edita_instituicao_cross_tenant_com_auditoria():
    superadmin, _ = criar_contas()
    escola = Instituicao.objects.create(nome="Escola Antiga", documento="00.000.000/0001-83")
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(
        reverse("painel-instituicao-editar", kwargs={"pk": escola.pk}),
        {
            "nome": "Escola Atualizada",
            "documento": "00.000.000/0001-84",
            "motivo": "correcao cadastral",
        },
    )

    assert resposta.status_code == 302
    escola.refresh_from_db()
    assert escola.nome == "Escola Atualizada"
    assert escola.documento == "00.000.000/0001-84"
    assert RegistroDeAuditoria.objects.filter(
        ator=superadmin, acao="editar_instituicao", objeto_id=str(escola.pk)
    ).exists()


def test_superadmin_arquiva_instituicao_desativa_contas_preserva_dados():
    superadmin, _ = criar_contas()
    escola = Instituicao.objects.create(nome="Escola Arquivada", documento="00.000.000/0001-85")
    aluno = get_user_model().objects.create_user(
        email="aluno-arquivado@escola.test", password="senha-segura-123",
        instituicao=escola, perfil=Perfil.ALUNO,
    )
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(
        reverse("painel-instituicao-arquivar", kwargs={"pk": escola.pk}),
        {"confirmacao": "on", "motivo": "encerramento do contrato"},
    )

    assert resposta.status_code == 302
    escola.refresh_from_db()
    aluno.refresh_from_db()
    assert escola.ativa is False
    assert aluno.is_active is False
    assert get_user_model().objects.filter(pk=aluno.pk).exists()
    assert RegistroDeAuditoria.objects.filter(
        ator=superadmin, acao="arquivar_instituicao", objeto_id=str(escola.pk)
    ).exists()


def test_superadmin_edita_usuario_de_outra_instituicao():
    superadmin, aluno = criar_contas()
    outra = Instituicao.objects.create(nome="Outra Escola", documento="00.000.000/0001-86")
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(
        reverse("painel-usuario-editar", kwargs={"pk": aluno.pk}),
        {
            "email": "aluno-atualizado@outra.test",
            "first_name": "Ana Atualizada",
            "last_name": "Teste",
            "instituicao": outra.pk,
            "perfil": Perfil.ALUNO,
            "ativo": "on",
            "motivo": "transferencia de instituicao",
        },
    )

    assert resposta.status_code == 302
    aluno.refresh_from_db()
    assert aluno.email == "aluno-atualizado@outra.test"
    assert aluno.instituicao == outra
    assert RegistroDeAuditoria.objects.filter(
        ator=superadmin, acao="editar_usuario", objeto_id=str(aluno.pk)
    ).exists()


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


def test_diretor_entra_no_painel_mas_nao_nas_rotas_de_plataforma():
    """Regra nova (2026-08-06): o painel e o mesmo site para todos os tiers.

    Antes o diretor levava 403 na porta. Agora ele entra e enxerga a propria
    escola; o que continua fechado sao as rotas de plataforma. O isolamento
    entre escolas esta coberto em `test_painel_por_hierarquia.py`.
    """
    escola = Instituicao.objects.create(nome="Escola diretor", documento="00.000.000/0001-72")
    diretor = get_user_model().objects.create_user(
        email="diretor-painel@escola.test", password="senha-segura-123",
        instituicao=escola, perfil=Perfil.DIRETOR,
    )
    cliente = Client()
    cliente.force_login(diretor)

    assert cliente.get(reverse("painel-dashboard")).status_code == 200
    assert cliente.get(reverse("painel-instituicoes")).status_code == 403
    assert cliente.get(reverse("painel-registros")).status_code == 403


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
