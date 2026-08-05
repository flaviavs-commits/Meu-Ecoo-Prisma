"""Regressao: o limite de uso e por competencia mensal, nao vitalicio.

Antes desta correcao `estado_cota` somava todo o `ConsumoIA` da conta desde
sempre. A conta que esgotasse o percentual num mes ficava bloqueada nos meses
seguintes mesmo com a escola sendo cobrada de novo.
"""

from datetime import datetime, timedelta, timezone as tz
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from contas.models import Instituicao, Perfil
from ia.models import ChamadaIA
from limites.ciclo import ciclo_atual, ciclo_de
from limites.excecoes import LimiteDeUsoExcedidoError
from limites.models import AssinaturaInstituicao, ConsumoIA, PlanoInstitucional
from limites.servico import autorizar_uso, estado_cota, registrar_uso

pytestmark = pytest.mark.django_db



def consumir(aluno, percentual):
    return registrar_uso(
        usuario=aluno,
        percentual=Decimal(percentual),
        fornecedor="falso",
        modelo="modelo",
        classe_tarefa="TUTORIA",
        referencia=ChamadaIA.objects.create(
            instituicao=aluno.instituicao, usuario=aluno
        ),
    )


def envelhecer(consumo, dias):
    """Joga o consumo para uma competencia anterior, como faria a virada do mes."""
    quando = timezone.now() - timedelta(days=dias)
    ConsumoIA.objects.filter(pk=consumo.pk).update(
        criado_em=quando, ciclo=ciclo_de(quando)
    )


def test_ciclo_de_usa_a_competencia_mensal_do_instante():
    assert ciclo_de(datetime(2026, 8, 5, 12, 0, tzinfo=tz.utc)) == "2026-08"
    assert ciclo_de(datetime(2026, 8, 31, 23, 59, tzinfo=tz.utc)) == "2026-08"
    assert ciclo_de(datetime(2026, 9, 1, 0, 0, tzinfo=tz.utc)) == "2026-09"


def test_consumo_do_mes_anterior_nao_bloqueia_o_mes_seguinte(aluno):
    envelhecer(consumir(aluno, "100"), dias=60)

    estado = estado_cota(aluno)

    assert estado.ciclo == ciclo_atual()
    assert estado.consumido_percentual == Decimal("0")
    assert estado.disponivel_percentual == Decimal("100")
    assert estado.bloqueado is False
    autorizar_uso(aluno)  # nao levanta


def test_consumo_do_mes_corrente_continua_bloqueando(aluno):
    consumir(aluno, "100")

    estado = estado_cota(aluno)

    assert estado.consumido_percentual == Decimal("100")
    assert estado.bloqueado is True
    with pytest.raises(LimiteDeUsoExcedidoError):
        autorizar_uso(aluno)


def test_debito_grava_a_competencia_aberta(aluno):
    consumo = consumir(aluno, "3")

    assert consumo.ciclo == ciclo_atual()


def test_limite_do_mes_anterior_esgotado_nao_recusa_debito_novo(aluno):
    """A checagem de `registrar_uso`, e nao so a leitura, respeita a janela."""
    envelhecer(consumir(aluno, "100"), dias=45)

    novo = consumir(aluno, "90")

    assert novo.ciclo == ciclo_atual()
    assert estado_cota(aluno).consumido_percentual == Decimal("90")


def test_historico_expoe_a_competencia_de_cada_consumo(aluno):
    antigo = consumir(aluno, "10")
    envelhecer(antigo, dias=40)
    consumir(aluno, "5")

    ciclos = set(ConsumoIA.objects.filter(usuario=aluno).values_list("ciclo", flat=True))

    assert len(ciclos) == 2
    assert ciclo_atual() in ciclos
