from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient

from contas.models import Instituicao, Perfil

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def limpar_throttle():
    cache.clear()


def usuario():
    escola = Instituicao.objects.create(nome="Escola Auth", documento="11.111.111/0001-11")
    return get_user_model().objects.create_user(
        email="aluno@auth.test", password="senha-segura-123", instituicao=escola,
        perfil=Perfil.ALUNO, data_nascimento=date(2010, 1, 1), first_name="Ana",
    )


def test_login_devolve_access_e_refresh_em_cookie():
    usuario()
    resposta = APIClient().post("/api/v1/auth/login/", {"email": "aluno@auth.test", "password": "senha-segura-123"})
    assert resposta.status_code == 200
    assert "access" in resposta.data
    assert "refresh" not in resposta.data
    assert resposta.cookies["refresh_token"]["httponly"] is True
    assert resposta.cookies["refresh_token"]["secure"] == ""


def test_login_invalido_tem_mensagem_generica():
    usuario()
    cliente = APIClient()
    errado = cliente.post("/api/v1/auth/login/", {"email": "aluno@auth.test", "password": "errada"})
    inexistente = cliente.post("/api/v1/auth/login/", {"email": "nao@existe.test", "password": "errada"})
    assert errado.status_code == inexistente.status_code == 401
    assert errado.data == inexistente.data


def test_rota_eu_exige_token():
    resposta = APIClient().get("/api/v1/auth/eu/")
    assert resposta.status_code == 401


def test_eu_retorna_identidade_sem_dados_sensiveis():
    pessoa = usuario()
    cliente = APIClient()
    login = cliente.post("/api/v1/auth/login/", {"email": pessoa.email, "password": "senha-segura-123"})
    cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
    resposta = cliente.get("/api/v1/auth/eu/")
    assert resposta.status_code == 200
    assert set(resposta.data) == {"id", "nome", "perfil", "instituicao_id"}


def test_refresh_usa_cookie_e_rotaciona_token():
    pessoa = usuario()
    cliente = APIClient()
    login = cliente.post("/api/v1/auth/login/", {"email": pessoa.email, "password": "senha-segura-123"})
    refresh = login.cookies["refresh_token"].value
    resposta = cliente.post("/api/v1/auth/refresh/", {}, HTTP_COOKIE=f"refresh_token={refresh}")
    assert resposta.status_code == 200
    assert "access" in resposta.data
    assert resposta.cookies["refresh_token"].value != refresh


def test_logout_invalida_cookie_de_refresh():
    pessoa = usuario()
    cliente = APIClient()
    login = cliente.post("/api/v1/auth/login/", {"email": pessoa.email, "password": "senha-segura-123"})
    cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
    cliente.cookies["refresh_token"] = login.cookies["refresh_token"].value

    resposta = cliente.post("/api/v1/auth/logout/", {})

    assert resposta.status_code == 204
    assert resposta.cookies["refresh_token"]["max-age"] == 0


def test_usuario_inativo_nao_entra():
    pessoa = usuario()
    pessoa.is_active = False
    pessoa.save(update_fields=["is_active"])
    resposta = APIClient().post("/api/v1/auth/login/", {"email": pessoa.email, "password": "senha-segura-123"})
    assert resposta.status_code == 401


def test_payload_do_token_tem_identidade_minima():
    pessoa = usuario()
    resposta = APIClient().post("/api/v1/auth/login/", {"email": pessoa.email, "password": "senha-segura-123"})
    from rest_framework_simplejwt.tokens import AccessToken
    token = AccessToken(resposta.data["access"])
    assert token["perfil"] == Perfil.ALUNO
    assert token["instituicao_id"] == pessoa.instituicao_id
    assert "email" not in token


def test_sexta_tentativa_de_login_e_bloqueada():
    pessoa = usuario()
    cliente = APIClient()
    for _ in range(5):
        cliente.post("/api/v1/auth/login/", {"email": pessoa.email, "password": "errada"})
    resposta = cliente.post("/api/v1/auth/login/", {"email": pessoa.email, "password": "errada"})
    assert resposta.status_code == 429
