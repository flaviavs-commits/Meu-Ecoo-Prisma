"""O painel é o mesmo site; o recorte é o da conta logada.

O que estes testes protegem é o isolamento entre escolas: um diretor entrando
no painel administrativo não pode, por rota nenhuma, ler conta de outra
instituição — nem receber 403 revelando que ela existe.
"""
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from contas.models import Instituicao, Perfil, TipoInstituicao
from ia.models import ChamadaIA
from limites.servico import registrar_uso

pytestmark = pytest.mark.django_db


@pytest.fixture
def escola():
    return Instituicao.objects.create(nome="Escola Alfa", documento="55.555.555/0001-55")


@pytest.fixture
def rival():
    return Instituicao.objects.create(nome="Escola Beta", documento="66.666.666/0001-66")


def _conta(instituicao, email, perfil):
    return get_user_model().objects.create_user(
        email=email, password="senha-segura-123", instituicao=instituicao, perfil=perfil
    )


@pytest.fixture
def diretor(escola):
    return _conta(escola, "diretor-painel@alfa.test", Perfil.DIRETOR)


@pytest.fixture
def aluno_da_escola(escola):
    return _conta(escola, "aluno-painel@alfa.test", Perfil.ALUNO)


@pytest.fixture
def aluno_rival(rival):
    return _conta(rival, "aluno-painel@beta.test", Perfil.ALUNO)


@pytest.fixture
def provider():
    instituicao, _ = Instituicao.objects.get_or_create(
        codigo="VITIS_SOULS",
        defaults={"nome": "Vitis Souls", "tipo": TipoInstituicao.PROVEDORA},
    )
    return get_user_model().objects.create_superuser(
        "provider-painel@vitissouls.test", "senha-segura-123", instituicao=instituicao
    )


@pytest.fixture
def administrador():
    prisma = Instituicao.objects.get(codigo="PRISMA")
    return _conta(prisma, "admin-painel@prisma.test", Perfil.ADMINISTRADOR)


def test_diretor_entra_no_painel(client, diretor):
    client.force_login(diretor)

    assert client.get(reverse("painel-dashboard")).status_code == 200


def test_aluno_e_professor_nao_entram_no_painel(client, escola):
    for email, perfil in (("a@alfa.test", Perfil.ALUNO), ("p@alfa.test", Perfil.PROFESSOR)):
        client.force_login(_conta(escola, email, perfil))

        assert client.get(reverse("painel-dashboard")).status_code == 403


def test_diretor_lista_so_as_contas_da_propria_escola(
    client, diretor, aluno_da_escola, aluno_rival
):
    client.force_login(diretor)

    corpo = client.get(reverse("painel-usuarios")).content.decode()

    assert aluno_da_escola.email in corpo
    assert aluno_rival.email not in corpo


def test_conta_de_outra_escola_e_indistinguivel_de_inexistente(client, diretor, aluno_rival):
    """404, não 403: 403 confirmaria que a conta existe."""
    client.force_login(diretor)

    resposta = client.get(reverse("painel-usuario", args=[aluno_rival.pk]))

    assert resposta.status_code == 404


def test_diretor_nao_abre_instituicao_alheia(client, diretor, rival, escola):
    client.force_login(diretor)

    assert client.get(reverse("painel-instituicao", args=[escola.pk])).status_code == 200
    assert client.get(reverse("painel-instituicao", args=[rival.pk])).status_code == 404


def test_diretor_nao_alcanca_as_rotas_de_plataforma(client, diretor, aluno_da_escola):
    client.force_login(diretor)

    restritas = [
        reverse("painel-instituicoes"),
        reverse("painel-contas-teste"),
        reverse("painel-registros"),
    ]
    for url in restritas:
        assert client.get(url).status_code == 403, url

    # Escrita de plataforma sobre a propria escola tambem e barrada.
    assert client.post(
        reverse("painel-usuario-perfil", args=[aluno_da_escola.pk]),
        {"perfil": Perfil.DIRETOR, "motivo": "tentativa"},
    ).status_code == 403
    assert client.post(
        reverse("painel-usuario-zerar-creditos", args=[aluno_da_escola.pk]),
        {"confirmacao": "on", "motivo": "tentativa"},
    ).status_code == 403


def test_diretor_desativa_conta_da_propria_escola(client, diretor, aluno_da_escola):
    client.force_login(diretor)

    resposta = client.post(
        reverse("painel-usuario-desativar", args=[aluno_da_escola.pk]),
        {"confirmacao": "on", "motivo": "saiu da escola"},
    )

    aluno_da_escola.refresh_from_db()
    assert resposta.status_code in (302, 200)
    assert aluno_da_escola.ativo is False


def test_diretor_nao_desativa_conta_de_outra_escola(client, diretor, aluno_rival):
    client.force_login(diretor)

    resposta = client.post(
        reverse("painel-usuario-desativar", args=[aluno_rival.pk]),
        {"confirmacao": "on", "motivo": "tentativa"},
    )

    aluno_rival.refresh_from_db()
    assert resposta.status_code == 404
    assert aluno_rival.ativo is True


def _consumir(usuario, percentual, fornecedor):
    registrar_uso(
        usuario=usuario,
        percentual=Decimal(percentual),
        fornecedor=fornecedor,
        modelo=f"modelo-{fornecedor}",
        classe_tarefa="TUTORIA",
        custo_bruto=Decimal("0.01"),
        referencia=ChamadaIA.objects.create(
            instituicao=usuario.instituicao, usuario=usuario
        ),
    )


def test_uso_do_diretor_mostra_so_a_propria_escola_e_sem_custo(
    client, diretor, aluno_da_escola, aluno_rival
):
    _consumir(aluno_da_escola, "10", "openrouter")
    _consumir(aluno_rival, "20", "claude")
    client.force_login(diretor)

    corpo = client.get(reverse("painel-uso")).content.decode()

    assert aluno_da_escola.email in corpo
    assert aluno_rival.email not in corpo
    # Custo em dolar e assunto da plataforma, nao da escola.
    assert "Custo (US$)" not in corpo
    assert "Contratos de fornecedor" not in corpo


def test_uso_do_provider_mostra_todas_as_escolas_e_o_custo(
    client, provider, aluno_da_escola, aluno_rival
):
    _consumir(aluno_da_escola, "10", "openrouter")
    _consumir(aluno_rival, "20", "claude")
    client.force_login(provider)

    corpo = client.get(reverse("painel-uso")).content.decode()

    assert aluno_da_escola.email in corpo
    assert aluno_rival.email in corpo
    assert "Custo (US$)" in corpo
    assert "Contratos de fornecedor" in corpo


def test_administrador_monitora_cross_tenant(client, administrador, aluno_da_escola, aluno_rival):
    _consumir(aluno_da_escola, "10", "openrouter")
    client.force_login(administrador)

    corpo = client.get(reverse("painel-uso")).content.decode()

    assert aluno_da_escola.email in corpo
    assert "Custo (US$)" in corpo


# --- Fronteira para cima: o diretor nao enxerga a equipe -----------------------
# Estes testes existem porque a regra de negocio e categorica: um diretor nao
# pode, por rota nenhuma, alcancar dado de um cargo acima do dele.


def test_diretor_nao_lista_contas_da_equipe(client, diretor, provider, administrador):
    client.force_login(diretor)

    corpo = client.get(reverse("painel-usuarios")).content.decode()

    assert provider.email not in corpo
    assert administrador.email not in corpo


def test_diretor_nao_abre_conta_da_equipe(client, diretor, provider, administrador):
    client.force_login(diretor)

    for conta in (provider, administrador):
        assert client.get(reverse("painel-usuario", args=[conta.pk])).status_code == 404


def test_diretor_nao_abre_as_instituicoes_internas(client, diretor):
    client.force_login(diretor)

    for codigo in ("VITIS_SOULS", "PRISMA"):
        interna = Instituicao.objects.get(codigo=codigo)
        assert client.get(reverse("painel-instituicao", args=[interna.pk])).status_code == 404


def test_diretor_nao_desativa_conta_da_equipe(client, diretor, provider, administrador):
    client.force_login(diretor)

    for conta in (provider, administrador):
        resposta = client.post(
            reverse("painel-usuario-desativar", args=[conta.pk]),
            {"confirmacao": "on", "motivo": "tentativa de escalada"},
        )
        conta.refresh_from_db()
        assert resposta.status_code == 404
        assert conta.ativo is True


def test_diretor_nao_ve_consumo_da_equipe_no_uso(client, diretor, provider):
    """Consumo de conta interna nao aparece no monitoramento da escola."""
    _consumir(provider, "5", "openrouter")
    client.force_login(diretor)

    corpo = client.get(reverse("painel-uso")).content.decode()

    assert provider.email not in corpo


def test_a_filtragem_por_perfil_nao_vaza_a_equipe(client, diretor, provider, administrador):
    """O filtro da listagem e aplicado DEPOIS do escopo, nunca no lugar dele."""
    client.force_login(diretor)

    for perfil in (Perfil.PROVIDER, Perfil.ADMINISTRADOR):
        corpo = client.get(reverse("painel-usuarios"), {"perfil": perfil}).content.decode()

        assert provider.email not in corpo
        assert administrador.email not in corpo
