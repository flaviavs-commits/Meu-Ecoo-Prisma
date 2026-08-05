import threading
from decimal import Decimal

import pytest
from django.db import close_old_connections, connection

from ia.models import ChamadaIA

from limites.excecoes import LimiteDeUsoExcedidoError
from limites.models import AssinaturaInstituicao, PlanoInstitucional
from limites.servico import autorizar_uso, registrar_uso, trava_cota

pytestmark = [
    pytest.mark.django_db(transaction=True),
    pytest.mark.skipif(
        connection.vendor == "sqlite",
        reason="concorrencia exige PostgreSQL; SQLite bloqueia a tabela inteira",
    ),
]


def test_duas_chamadas_nao_consumem_a_mesma_cota_em_paralelo(instituicao, aluno):
    plano = PlanoInstitucional.objects.get(codigo="PRISMA")
    plano.limite_percentual_por_conta = Decimal("2")
    plano.save(update_fields=["limite_percentual_por_conta"])
    AssinaturaInstituicao.objects.create(instituicao=instituicao, plano=plano)
    referencias = [
        ChamadaIA.objects.create(instituicao=instituicao, usuario=aluno)
        for _ in range(2)
    ]
    barreira = threading.Barrier(2)
    concluidas = []
    recusadas = []
    falhas = []

    def consumir(referencia):
        close_old_connections()
        try:
            barreira.wait(timeout=5)
            with trava_cota(aluno):
                autorizar_uso(aluno)
                registrar_uso(
                    usuario=aluno,
                    percentual=Decimal("2"),
                    fornecedor="falso",
                    modelo="modelo",
                    classe_tarefa="TUTORIA",
                    referencia=referencia,
                )
                concluidas.append(referencia.pk)
        except LimiteDeUsoExcedidoError:
            recusadas.append(referencia.pk)
        except Exception as erro:  # pragma: no cover - falha inesperada aparece abaixo
            falhas.append(erro)
        finally:
            close_old_connections()

    threads = [threading.Thread(target=consumir, args=(referencia,)) for referencia in referencias]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)

    assert all(not thread.is_alive() for thread in threads)
    assert falhas == []
    assert len(concluidas) == 1
    assert len(recusadas) == 1
