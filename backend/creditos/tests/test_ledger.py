from decimal import Decimal

import pytest

from creditos.excecoes import SaldoInsuficienteError
from creditos.models import Lancamento, LancamentoImutavelError, TipoLancamento
from creditos.saldo import saldo_instituicao, saldo_usuario
from creditos.consumo import autorizar_consumo, registrar_consumo, trava_saldo
from creditos.alerta import estado_alerta_usuario
from creditos.models import ConfiguracaoAlertaSaldo

pytestmark = pytest.mark.django_db


def test_saldo_instituicao_sem_lancamento_e_zero(instituicao):
    assert saldo_instituicao(instituicao.id) == Decimal("0")


def test_credito_soma_debito_subtrai(instituicao, aluno):
    Lancamento.objects.create(
        instituicao=instituicao, usuario=aluno, tipo=TipoLancamento.CREDITO,
        quantidade=Decimal("10"), motivo="carga inicial",
    )
    Lancamento.objects.create(
        instituicao=instituicao, usuario=aluno, tipo=TipoLancamento.DEBITO,
        quantidade=Decimal("3"), motivo="consumo",
    )
    assert saldo_usuario(aluno.id) == Decimal("7")


def test_save_em_lancamento_existente_levanta_excecao(instituicao, aluno):
    lanc = Lancamento.objects.create(
        instituicao=instituicao, usuario=aluno, tipo=TipoLancamento.CREDITO,
        quantidade=Decimal("10"), motivo="carga",
    )
    lanc.motivo = "tentando editar"
    with pytest.raises(LancamentoImutavelError):
        lanc.save()


def test_delete_em_lancamento_levanta_excecao(instituicao, aluno):
    lanc = Lancamento.objects.create(
        instituicao=instituicao, usuario=aluno, tipo=TipoLancamento.CREDITO,
        quantidade=Decimal("10"), motivo="carga",
    )
    with pytest.raises(LancamentoImutavelError):
        lanc.delete()


def test_saldo_zero_recusa_com_saldo_insuficiente(instituicao, aluno):
    with trava_saldo(aluno):
        with pytest.raises(SaldoInsuficienteError):
            autorizar_consumo(aluno)


def test_saldo_positivo_autoriza_mesmo_com_custo_maior_e_negativa(instituicao, aluno):
    Lancamento.objects.create(
        instituicao=instituicao, usuario=aluno, tipo=TipoLancamento.CREDITO,
        quantidade=Decimal("5"), motivo="carga",
    )
    with trava_saldo(aluno):
        saldo = autorizar_consumo(aluno)
        assert saldo == Decimal("5")
    registrar_consumo(
        instituicao=instituicao, usuario=aluno, quantidade=Decimal("8"),
        motivo="chamada cara", referencia=None,
    )
    assert saldo_usuario(aluno.id) == Decimal("-3")


def test_chamada_que_falhou_nao_gera_debito(instituicao, aluno):
    Lancamento.objects.create(
        instituicao=instituicao, usuario=aluno, tipo=TipoLancamento.CREDITO,
        quantidade=Decimal("5"), motivo="carga",
    )
    with trava_saldo(aluno):
        autorizar_consumo(aluno)
        # simula falha na chamada de IA: nenhum debito e registrado
    assert saldo_usuario(aluno.id) == Decimal("5")


def test_mesma_referencia_nao_debita_duas_vezes(instituicao, aluno, django_settings=None):
    from django.apps import apps

    ChamadaIA = apps.get_model("ia", "ChamadaIA")
    chamada = ChamadaIA.objects.create()
    registrar_consumo(
        instituicao=instituicao, usuario=aluno, quantidade=Decimal("4"),
        motivo="chamada", referencia=chamada,
    )
    registrar_consumo(
        instituicao=instituicao, usuario=aluno, quantidade=Decimal("4"),
        motivo="retry", referencia=chamada,
    )
    debitos = Lancamento.objects.filter(referencia=chamada, tipo=TipoLancamento.DEBITO)
    assert debitos.count() == 1


def test_aluno_nao_ve_saldo_de_outro_aluno(instituicao, aluno, outro_aluno):
    Lancamento.objects.create(
        instituicao=instituicao, usuario=aluno, tipo=TipoLancamento.CREDITO,
        quantidade=Decimal("10"), motivo="carga",
    )
    assert saldo_usuario(outro_aluno.id) == Decimal("0")
    assert saldo_usuario(aluno.id) == Decimal("10")


def test_alerta_calcula_saldo_baixo_sem_coluna_mutavel(instituicao, aluno):
    ConfiguracaoAlertaSaldo.objects.create(
        instituicao=instituicao, limiar=Decimal("5")
    )
    Lancamento.objects.create(
        instituicao=instituicao,
        usuario=aluno,
        tipo=TipoLancamento.CREDITO,
        quantidade=Decimal("3"),
        motivo="carga",
    )

    assert estado_alerta_usuario(aluno) == {
        "saldo": Decimal("3"),
        "limiar": Decimal("5"),
        "saldo_baixo": True,
    }
