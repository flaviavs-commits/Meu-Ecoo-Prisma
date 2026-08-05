"""Regressao: arquivar instituicao era irreversivel e sem rastro por conta.

O `update()` em massa desativava todas as contas sem gravar quais estavam
ativas antes. Depois do ato ninguem sabia o que desfazer, e reativar tudo
ressuscitaria tambem quem ja estava inativo por outro motivo.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from contas.auditoria import RegistroDeAuditoria
from contas.models import Instituicao, Perfil
from painel_admin.services.arquivar_instituicao import (
    ACAO_DESATIVAR_CONTA,
    ACAO_REATIVAR_CONTA,
    ArquivamentoInstituicaoNegado,
    arquivar_instituicao,
    desarquivar_instituicao,
)
from painel_admin.services.editar_usuario import UsuarioEdicaoNegada, editar_usuario

pytestmark = pytest.mark.django_db


@pytest.fixture
def superadmin(db):
    return get_user_model().objects.create_superuser(
        email="admin-arquivamento@prisma.test", password="senha-segura-123"
    )


@pytest.fixture
def escola(db):
    return Instituicao.objects.create(
        nome="Escola Arquivavel", documento="00.000.000/0001-90"
    )


def conta(escola, sufixo, ativa=True):
    return get_user_model().objects.create_user(
        email=f"conta-{sufixo}@escola.test",
        password="senha-segura-123",
        instituicao=escola,
        perfil=Perfil.ALUNO,
        ativo=ativa,
        is_active=ativa,
    )


def test_arquivar_registra_auditoria_por_conta_atingida(superadmin, escola):
    ana = conta(escola, "ana")
    bruno = conta(escola, "bruno")

    arquivar_instituicao(
        alvo=escola, ator=superadmin, confirmado=True, motivo="fim de contrato"
    )

    auditados = set(
        RegistroDeAuditoria.objects.filter(
            acao=ACAO_DESATIVAR_CONTA, objeto_tipo="Usuario"
        ).values_list("objeto_id", flat=True)
    )
    assert auditados == {str(ana.pk), str(bruno.pk)}


def test_desarquivar_reativa_exatamente_quem_o_arquivamento_derrubou(superadmin, escola):
    ativa = conta(escola, "ativa")
    ja_inativa = conta(escola, "ja-inativa", ativa=False)
    arquivar_instituicao(
        alvo=escola, ator=superadmin, confirmado=True, motivo="fim de contrato"
    )

    desarquivar_instituicao(
        alvo=escola, ator=superadmin, confirmado=True, motivo="contrato renovado"
    )

    escola.refresh_from_db()
    ativa.refresh_from_db()
    ja_inativa.refresh_from_db()
    assert escola.ativa is True
    assert ativa.is_active is True and ativa.ativo is True
    # A conta que ja estava inativa antes do arquivamento nao pode voltar so
    # porque a escola reabriu: ela foi desativada por outro motivo.
    assert ja_inativa.is_active is False
    assert RegistroDeAuditoria.objects.filter(
        acao=ACAO_REATIVAR_CONTA, objeto_id=str(ativa.pk)
    ).exists()


def test_desarquivar_ignora_desativacao_individual_entre_dois_ciclos(superadmin, escola):
    pessoa = conta(escola, "pessoa")
    arquivar_instituicao(alvo=escola, ator=superadmin, confirmado=True, motivo="ciclo 1")
    desarquivar_instituicao(alvo=escola, ator=superadmin, confirmado=True, motivo="volta 1")
    # Entre os dois ciclos, a conta e desativada individualmente.
    get_user_model().objects.filter(pk=pessoa.pk).update(ativo=False, is_active=False)
    arquivar_instituicao(alvo=escola, ator=superadmin, confirmado=True, motivo="ciclo 2")

    desarquivar_instituicao(alvo=escola, ator=superadmin, confirmado=True, motivo="volta 2")

    pessoa.refresh_from_db()
    assert pessoa.is_active is False


def test_conta_transferida_para_outra_escola_nao_volta(superadmin, escola):
    pessoa = conta(escola, "transferida")
    arquivar_instituicao(alvo=escola, ator=superadmin, confirmado=True, motivo="ciclo")
    outra = Instituicao.objects.create(
        nome="Escola Destino", documento="00.000.000/0001-91"
    )
    get_user_model().objects.filter(pk=pessoa.pk).update(instituicao=outra)

    desarquivar_instituicao(alvo=escola, ator=superadmin, confirmado=True, motivo="volta")

    pessoa.refresh_from_db()
    assert pessoa.is_active is False


def test_desarquivar_exige_confirmacao_e_motivo(superadmin, escola):
    arquivar_instituicao(alvo=escola, ator=superadmin, confirmado=True, motivo="ciclo")

    with pytest.raises(ArquivamentoInstituicaoNegado):
        desarquivar_instituicao(
            alvo=escola, ator=superadmin, confirmado=False, motivo="volta"
        )
    with pytest.raises(ArquivamentoInstituicaoNegado):
        desarquivar_instituicao(alvo=escola, ator=superadmin, confirmado=True, motivo="  ")

    escola.refresh_from_db()
    assert escola.ativa is False


def test_desarquivar_instituicao_ja_ativa_e_recusado(superadmin, escola):
    with pytest.raises(ArquivamentoInstituicaoNegado):
        desarquivar_instituicao(
            alvo=escola, ator=superadmin, confirmado=True, motivo="volta"
        )


def test_rota_de_desarquivamento_reabre_pelo_painel(superadmin, escola):
    pessoa = conta(escola, "pelo-painel")
    arquivar_instituicao(alvo=escola, ator=superadmin, confirmado=True, motivo="ciclo")
    cliente = Client()
    cliente.force_login(superadmin)

    resposta = cliente.post(
        reverse("painel-instituicao-desarquivar", kwargs={"pk": escola.pk}),
        {"confirmacao": "on", "motivo": "contrato renovado"},
    )

    escola.refresh_from_db()
    pessoa.refresh_from_db()
    assert resposta.status_code == 302
    assert escola.ativa is True
    assert pessoa.is_active is True


def test_rota_de_desarquivamento_exige_superadmin(escola):
    _, aluno = escola, conta(escola, "sem-poder")
    cliente = Client()
    cliente.force_login(aluno)

    resposta = cliente.post(
        reverse("painel-instituicao-desarquivar", kwargs={"pk": escola.pk}),
        {"confirmacao": "on", "motivo": "tentativa"},
    )

    assert resposta.status_code == 403


def test_get_em_rota_destrutiva_passa_pelo_portao_antes_do_metodo(escola):
    """Ordem dos decoradores: anonimo nao pode descobrir a rota por um 405."""
    resposta = Client().get(
        reverse("painel-instituicao-arquivar", kwargs={"pk": escola.pk})
    )

    assert resposta.status_code != 405


def test_edicao_recusa_email_que_difere_so_por_maiuscula(superadmin, escola):
    """Regressao: igualdade exata deixava passar `ana@x` sobre um `Ana@x` ja
    existente, criando duas contas indistinguiveis no login."""
    get_user_model().objects.create_user(
        email="Ana@escola.test", password="senha-segura-123",
        instituicao=escola, perfil=Perfil.ALUNO,
    )
    outra = conta(escola, "outra")

    with pytest.raises(UsuarioEdicaoNegada):
        editar_usuario(
            alvo=outra, ator=superadmin, email="ana@escola.test", nome="Outra",
            sobrenome="", instituicao=escola, perfil=Perfil.ALUNO, ativo=True,
            motivo="tentativa de colisao",
        )
