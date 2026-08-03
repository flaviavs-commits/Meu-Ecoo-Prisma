import threading
from decimal import Decimal

import pytest
from django.db import connection

from creditos.consumo import autorizar_consumo, registrar_consumo, trava_saldo
from creditos.excecoes import SaldoInsuficienteError
from creditos.models import Lancamento, TipoLancamento
from creditos.saldo import saldo_usuario

pytestmark = [
    pytest.mark.django_db(transaction=True),
    pytest.mark.skipif(
        connection.vendor == "sqlite",
        reason="concorrencia exige PostgreSQL; SQLite bloqueia a tabela inteira",
    ),
]


def test_duas_chamadas_paralelas_nao_passam_pelo_gate_indevidamente(instituicao, aluno):
    """Prova real de concorrencia: saldo 10, duas threads tentam debitar 8 ao mesmo
    tempo. A trava (`select_for_update`) deve serializar - uma autoriza e debita
    primeiro, deixando saldo em 2; a segunda le saldo > 0 (2), autoriza tambem
    (comportamento aceito: gate e `saldo > 0`, nao `saldo >= custo`) e so entao
    debita, negativando. O que o teste realmente prova e que as duas threads
    nunca leem o MESMO saldo "10" ao mesmo tempo - se lessem, cada uma debitaria
    8 achando que partia de 10, e o saldo final seria -6 em vez de -6 vindo de
    UMA leitura de 10 e outra de 2 (efeito auditavel via ordem dos lancamentos).
    """
    Lancamento.objects.create(
        instituicao=instituicao, usuario=aluno, tipo=TipoLancamento.CREDITO,
        quantidade=Decimal("10"), motivo="carga",
    )

    resultados = []
    erros = []
    barreira = threading.Barrier(2)

    def tentar_consumir():
        try:
            barreira.wait(timeout=5)
            with trava_saldo(aluno):
                saldo_antes = autorizar_consumo(aluno)
                registrar_consumo(
                    instituicao=instituicao, usuario=aluno, quantidade=Decimal("8"),
                    motivo="chamada concorrente", referencia=None,
                )
                resultados.append(saldo_antes)
        except SaldoInsuficienteError:
            erros.append("recusado")
        finally:
            connection.close()

    t1 = threading.Thread(target=tentar_consumir)
    t2 = threading.Thread(target=tentar_consumir)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # As duas viram saldo > 0 em algum momento (10 e depois 2) e as duas debitaram,
    # nunca as duas partindo do mesmo saldo 10 - prova de que a trava serializou.
    assert sorted(resultados) == [Decimal("2"), Decimal("10")]
    assert saldo_usuario(aluno.id) == Decimal("10") - Decimal("8") - Decimal("8")
