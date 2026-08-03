from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from creditos.models import Lancamento, TipoLancamento

pytestmark = pytest.mark.django_db


def cliente_autenticado(usuario):
    cliente = APIClient()
    cliente.force_authenticate(user=usuario)
    return cliente


def test_aluno_consulta_o_proprio_saldo(instituicao, aluno):
    Lancamento.objects.create(
        instituicao=instituicao,
        usuario=aluno,
        tipo=TipoLancamento.CREDITO,
        quantidade=Decimal("7"),
        motivo="carga",
    )

    resposta = cliente_autenticado(aluno).get("/api/v1/creditos/saldo/")

    assert resposta.status_code == 200
    assert resposta.json()["saldo"] == "7.0000"


def test_aluno_consulta_alerta_de_saldo(instituicao, aluno):
    from creditos.models import ConfiguracaoAlertaSaldo

    ConfiguracaoAlertaSaldo.objects.create(instituicao=instituicao, limiar=Decimal("5"))

    resposta = cliente_autenticado(aluno).get("/api/v1/creditos/saldo/alerta/")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "saldo": "0.0000",
        "limiar": "5.0000",
        "saldo_baixo": True,
    }


def test_aluno_nao_consulta_saldo_da_instituicao(instituicao, aluno):
    resposta = cliente_autenticado(aluno).get("/api/v1/creditos/saldo/instituicao/")

    assert resposta.status_code == 403


def test_diretor_consulta_saldo_da_propria_instituicao(instituicao, diretor):
    Lancamento.objects.create(
        instituicao=instituicao,
        tipo=TipoLancamento.CREDITO,
        quantidade=Decimal("12"),
        motivo="pool",
    )

    resposta = cliente_autenticado(diretor).get("/api/v1/creditos/saldo/instituicao/")

    assert resposta.status_code == 200
    assert resposta.json()["saldo"] == "12.0000"


def test_lancamentos_de_aluno_ficam_limitados_ao_proprio_usuario(
    instituicao, aluno, outro_aluno
):
    Lancamento.objects.create(
        instituicao=instituicao,
        usuario=aluno,
        tipo=TipoLancamento.CREDITO,
        quantidade=Decimal("3"),
        motivo="proprio",
    )
    Lancamento.objects.create(
        instituicao=instituicao,
        usuario=outro_aluno,
        tipo=TipoLancamento.CREDITO,
        quantidade=Decimal("9"),
        motivo="outro",
    )

    resposta = cliente_autenticado(aluno).get("/api/v1/creditos/lancamentos/")

    assert resposta.status_code == 200
    assert [item["usuario"] for item in resposta.json()["results"]] == [aluno.id]


def test_alocacao_exige_diretor(instituicao, aluno):
    resposta = cliente_autenticado(aluno).post(
        "/api/v1/creditos/alocacoes/",
        {"destino_usuario": aluno.id, "quantidade": "2", "motivo": "carga"},
        format="json",
    )

    assert resposta.status_code == 403


def test_diretor_aloca_creditos_para_usuario(instituicao, aluno, diretor):
    resposta = cliente_autenticado(diretor).post(
        "/api/v1/creditos/alocacoes/",
        {"destino_usuario": aluno.id, "quantidade": "2", "motivo": "carga"},
        format="json",
    )

    assert resposta.status_code == 201
    assert Lancamento.objects.filter(instituicao=instituicao).count() == 2


def test_reducao_sem_confirmacao_retorna_400(instituicao, aluno, diretor):
    resposta = cliente_autenticado(diretor).post(
        "/api/v1/creditos/alocacoes/reduzir/",
        {
            "origem_usuario": aluno.id,
            "quantidade": "1",
            "motivo": "ajuste",
        },
        format="json",
    )

    assert resposta.status_code == 400
