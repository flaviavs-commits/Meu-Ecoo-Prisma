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
from contas.models import Instituicao, Perfil
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
