from decimal import Decimal
from io import StringIO

import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.core.management import call_command
from django.urls import reverse
from rest_framework.test import APIClient

from contas.auditoria import RegistroDeAuditoria
from contas.convites import ConviteProfessor, convite_professor
from contas.models import Instituicao, Perfil, TipoInstituicao
from creditos.models import Lancamento, TipoLancamento


pytestmark = pytest.mark.django_db


def argumentos_onboarding(**extras):
    argumentos = {
        "nome": "Colegio Exemplo",
        "documento": "00.000.000/0001-90",
        "diretor_email": "diretor@exemplo.edu.br",
        "diretor_nome": "Diretor Exemplo",
        "creditos_iniciais": "100000",
    }
    argumentos.update(extras)
    return argumentos


def criar_diretor(email="diretor@escola.test", documento="00.000.000/0001-91"):
    escola = Instituicao.objects.create(nome="Escola", documento=documento)
    diretor = get_user_model().objects.create_user(
        email=email,
        password="senha-segura-123",
        first_name="Diretor",
        instituicao=escola,
        perfil=Perfil.DIRETOR,
    )
    return escola, diretor


def test_comando_cria_instituicao_diretor_e_credito_em_uma_transacao():
    call_command("criar_instituicao", **argumentos_onboarding())

    escola = Instituicao.objects.get(documento="00.000.000/0001-90")
    diretor = get_user_model().objects.get(email="diretor@exemplo.edu.br")
    lancamento = Lancamento.objects.get(instituicao=escola)

    assert diretor.instituicao == escola
    assert diretor.perfil == Perfil.DIRETOR
    assert diretor.has_usable_password() is False
    assert lancamento.tipo == TipoLancamento.CREDITO
    assert lancamento.quantidade == Decimal("100000")


def test_comando_invalido_faz_rollback_completo():
    with pytest.raises(Exception):
        call_command("criar_instituicao", **argumentos_onboarding(creditos_iniciais="-1"))

    assert Instituicao.objects.filter(documento="00.000.000/0001-90").exists() is False
    assert get_user_model().objects.filter(email="diretor@exemplo.edu.br").exists() is False
    assert Lancamento.objects.exists() is False


def test_comando_repetido_falha_com_mensagem_clara_e_nao_duplica():
    call_command("criar_instituicao", **argumentos_onboarding())
    saida = StringIO()

    with pytest.raises(Exception, match="documento|já existe|ja existe"):
        call_command("criar_instituicao", stdout=saida, **argumentos_onboarding())

    assert Instituicao.objects.filter(documento="00.000.000/0001-90").count() == 1
    assert Lancamento.objects.count() == 1


def test_diretor_nao_tem_senha_utilizavel_nem_acesso_ao_admin():
    call_command("criar_instituicao", **argumentos_onboarding())
    diretor = get_user_model().objects.get(email="diretor@exemplo.edu.br")

    assert diretor.is_staff is False
    assert admin.site.has_permission(type("Request", (), {"user": diretor})()) is False


def test_superuser_manager_vincula_tier_provider_a_vitis_souls():
    equipe = get_user_model().objects.create_superuser(
        email="equipe-vitis@interno.test", password="senha-segura-123"
    )

    assert equipe.perfil == Perfil.PROVIDER
    assert equipe.instituicao.codigo == "VITIS_SOULS"
    assert equipe.instituicao.tipo == TipoInstituicao.PROVEDORA
    assert equipe.instituicao.documento is None


def test_admin_preserva_vitis_e_nao_oferece_exclusao_fisica():
    equipe = get_user_model().objects.create_superuser(
        email="equipe-admin@interno.test", password="senha-segura-123"
    )
    instituicao_admin = admin.site._registry[Instituicao]
    usuario_admin = admin.site._registry[get_user_model()]

    assert instituicao_admin.has_change_permission(None, equipe.instituicao) is False
    assert instituicao_admin.has_delete_permission(None, equipe.instituicao) is False
    assert usuario_admin.has_delete_permission(None, equipe) is False


def test_lancamento_e_auditoria_sao_somente_leitura_no_admin():
    assert admin.site._registry[Lancamento].has_change_permission(None) is False
    assert admin.site._registry[Lancamento].has_delete_permission(None) is False
    assert admin.site._registry[RegistroDeAuditoria].has_change_permission(None) is False
    assert admin.site._registry[RegistroDeAuditoria].has_delete_permission(None) is False


def test_desativar_sem_confirmacao_retorna_400():
    escola, diretor = criar_diretor()
    alvo = get_user_model().objects.create_user(
        email="professor@escola.test",
        password="senha-segura-123",
        instituicao=escola,
        perfil=Perfil.PROFESSOR,
    )
    cliente = APIClient()
    cliente.force_authenticate(diretor)

    resposta = cliente.post(
        reverse("desativar-usuario", kwargs={"pk": alvo.pk}),
        {"motivo": "encerramento do vinculo"},
        format="json",
    )

    assert resposta.status_code == 400
    alvo.refresh_from_db()
    assert alvo.ativo is True


def test_desativar_preserva_usuario_desativa_login_e_audita():
    escola, diretor = criar_diretor(documento="00.000.000/0001-92")
    alvo = get_user_model().objects.create_user(
        email="professor2@escola.test",
        password="senha-segura-123",
        instituicao=escola,
        perfil=Perfil.PROFESSOR,
    )
    cliente = APIClient()
    cliente.force_authenticate(diretor)

    resposta = cliente.post(
        reverse("desativar-usuario", kwargs={"pk": alvo.pk}),
        {"confirmacao": True, "motivo": "encerramento do vinculo"},
        format="json",
    )

    assert resposta.status_code == 204
    alvo.refresh_from_db()
    assert alvo.ativo is False
    assert alvo.is_active is False
    assert get_user_model().objects.filter(pk=alvo.pk).exists()
    assert RegistroDeAuditoria.objects.filter(
        objeto_tipo="Usuario", objeto_id=str(alvo.pk), motivo="encerramento do vinculo"
    ).exists()
    assert authenticate(email=alvo.email, password="senha-segura-123") is None


def test_convite_cria_estado_pendente_sem_usuario_ativo():
    escola, diretor = criar_diretor(documento="00.000.000/0001-93")

    convite = convite_professor(
        instituicao=escola,
        email="novo.professor@escola.test",
        convidado_por=diretor,
    )

    assert convite.status == ConviteProfessor.Status.PENDENTE
    assert convite.aceito_em is None
    assert get_user_model().objects.filter(email=convite.email).exists() is False
    assert convite.token_hash


def test_admin_tem_url_propria_e_diretor_nao_entra():
    escola, diretor = criar_diretor(documento="00.000.000/0001-94")
    assert escola
    resposta = APIClient().get("/admin/")
    assert resposta.status_code == 404
    assert admin.site.has_permission(type("Request", (), {"user": diretor})()) is False

    equipe = get_user_model().objects.create_superuser(
        email="equipe@interno.test", password="senha-segura-123"
    )
    cliente = APIClient()
    assert cliente.login(email=equipe.email, password="senha-segura-123")
    assert cliente.get(reverse("admin:index")).status_code == 200
    assert cliente.get(reverse("admin:contas_instituicao_changelist")).status_code == 200

    cache.clear()
    login_cliente = APIClient()
    for _ in range(5):
        assert login_cliente.post(reverse("admin:login"), {"username": equipe.email, "password": "errada"}).status_code == 200
    assert login_cliente.post(reverse("admin:login"), {"username": equipe.email, "password": "errada"}).status_code == 429


def test_listagens_admin_nao_exibem_hash_de_senha_ou_conteudo_sensivel():
    usuario_admin = admin.site._registry[get_user_model()]
    assert "password" not in usuario_admin.list_display
    assert not any("senha" in str(campo).lower() for campo in usuario_admin.get_fields(None))
    chamada_admin = admin.site._registry[
        __import__("ia.models", fromlist=["ChamadaIA"]).ChamadaIA
    ]
    assert "prompt" not in chamada_admin.list_display
    assert "resposta" not in chamada_admin.list_display

# --- Isolamento entre instituicoes na desativacao (revisao 2026-08-05) ---
#
# `is_staff` (booleano comum, marcavel pelo Django Admin) curto-circuitava a
# checagem de permissao e o filtro de tenant da view, deixando qualquer conta
# com a flag desativar usuario de QUALQUER instituicao. O superadmin e o unico
# papel cross-tenant do produto. Ver
# `docs/REVISAO-2026-08-05-SEGURANCA-E-INTEGRACAO.md`.


def criar_staff_nao_superadmin(escola, email="staff@escola.test"):
    return get_user_model().objects.create_user(
        email=email, password="senha-segura-123", instituicao=escola,
        perfil=Perfil.PROFESSOR, is_staff=True,
    )


def test_staff_nao_superadmin_nao_desativa_usuario_de_outra_instituicao():
    _, diretor_a = criar_diretor(email="dir-a@escola.test", documento="00.000.000/0001-A1")
    escola_b, diretor_b = criar_diretor(email="dir-b@escola.test", documento="00.000.000/0001-B1")
    atacante = criar_staff_nao_superadmin(diretor_a.instituicao)
    cliente = APIClient()
    cliente.force_authenticate(atacante)

    resposta = cliente.post(
        reverse("desativar-usuario", kwargs={"pk": diretor_b.pk}),
        {"confirmacao": True, "motivo": "atravessando o tenant"}, format="json",
    )

    assert resposta.status_code == 404  # nem existe, do ponto de vista dele
    diretor_b.refresh_from_db()
    assert diretor_b.ativo is True
    assert escola_b.usuarios.filter(ativo=False).count() == 0


def test_staff_nao_superadmin_nao_desativa_nem_na_propria_instituicao():
    escola, _ = criar_diretor(email="dir-c@escola.test", documento="00.000.000/0001-C1")
    atacante = criar_staff_nao_superadmin(escola, email="staff-c@escola.test")
    colega = get_user_model().objects.create_user(
        email="colega-c@escola.test", password="senha-segura-123",
        instituicao=escola, perfil=Perfil.ALUNO,
    )
    cliente = APIClient()
    cliente.force_authenticate(atacante)

    resposta = cliente.post(
        reverse("desativar-usuario", kwargs={"pk": colega.pk}),
        {"confirmacao": True, "motivo": "sem permissao para isto"}, format="json",
    )

    assert resposta.status_code == 403
    colega.refresh_from_db()
    assert colega.ativo is True


def test_diretor_nao_desativa_usuario_de_outra_instituicao():
    _, diretor_a = criar_diretor(email="dir-d@escola.test", documento="00.000.000/0001-D1")
    _, diretor_b = criar_diretor(email="dir-e@escola.test", documento="00.000.000/0001-E1")
    cliente = APIClient()
    cliente.force_authenticate(diretor_a)

    resposta = cliente.post(
        reverse("desativar-usuario", kwargs={"pk": diretor_b.pk}),
        {"confirmacao": True, "motivo": "fora do meu tenant"}, format="json",
    )

    assert resposta.status_code == 404
    diretor_b.refresh_from_db()
    assert diretor_b.ativo is True


def test_superadmin_desativa_cross_tenant():
    _, diretor = criar_diretor(email="dir-f@escola.test", documento="00.000.000/0001-F1")
    superadmin = get_user_model().objects.create_superuser(
        email="super@prisma.test", password="senha-segura-123",
    )
    cliente = APIClient()
    cliente.force_authenticate(superadmin)

    resposta = cliente.post(
        reverse("desativar-usuario", kwargs={"pk": diretor.pk}),
        {"confirmacao": True, "motivo": "papel cross-tenant legitimo"}, format="json",
    )

    assert resposta.status_code == 204
    diretor.refresh_from_db()
    assert diretor.ativo is False


def test_usuarios_sem_instituicao_nao_sao_o_mesmo_tenant():
    """`instituicao_id` e anulavel: None == None nao pode virar 'mesma escola'."""
    orfao_ator = get_user_model().objects.create_user(
        email="orfao-ator@sem.test", password="senha-segura-123", perfil=Perfil.DIRETOR,
    )
    orfao_alvo = get_user_model().objects.create_user(
        email="orfao-alvo@sem.test", password="senha-segura-123", perfil=Perfil.ALUNO,
    )
    cliente = APIClient()
    cliente.force_authenticate(orfao_ator)

    resposta = cliente.post(
        reverse("desativar-usuario", kwargs={"pk": orfao_alvo.pk}),
        {"confirmacao": True, "motivo": "os dois sem instituicao"}, format="json",
    )

    assert resposta.status_code == 403
    orfao_alvo.refresh_from_db()
    assert orfao_alvo.ativo is True
