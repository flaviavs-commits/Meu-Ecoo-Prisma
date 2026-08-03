from decimal import Decimal

import pytest

from creditos.alocacao import alocar, reduzir_alocacao
from creditos.excecoes import (
    AlocacaoForaDaInstituicaoError,
    AlocacaoSemConfirmacaoError,
)
from creditos.models import Lancamento, TipoLancamento
from contas.auditoria import RegistroDeAuditoria
from contas.models import Instituicao
from academico.models import Turma

pytestmark = pytest.mark.django_db


def test_alocacao_move_dos_dois_lados_na_mesma_transacao(instituicao, aluno):
    saida, entrada = alocar(
        instituicao=instituicao, destino_usuario=aluno, quantidade=Decimal("20"),
        motivo="alocacao inicial", criado_por=aluno,
    )
    assert saida.tipo == TipoLancamento.DEBITO
    assert saida.usuario is None
    assert entrada.tipo == TipoLancamento.ALOCACAO
    assert entrada.usuario_id == aluno.id
    assert Lancamento.objects.filter(instituicao=instituicao).count() == 2


def test_reducao_de_alocacao_sem_confirmacao_recusa(instituicao, aluno):
    alocar(
        instituicao=instituicao, destino_usuario=aluno, quantidade=Decimal("20"),
        motivo="alocacao inicial", criado_por=aluno,
    )
    with pytest.raises(AlocacaoSemConfirmacaoError):
        reduzir_alocacao(
            instituicao=instituicao, origem_usuario=aluno, quantidade=Decimal("5"),
            motivo="ajuste", criado_por=aluno, confirmado=False,
        )


def test_reducao_confirmada_grava_auditoria(instituicao, aluno, diretor):
    alocar(
        instituicao=instituicao, destino_usuario=aluno, quantidade=Decimal("20"),
        motivo="alocacao inicial", criado_por=diretor,
    )

    reduzir_alocacao(
        instituicao=instituicao, origem_usuario=aluno, quantidade=Decimal("5"),
        motivo="ajuste de limite", criado_por=diretor, confirmado=True,
    )

    assert RegistroDeAuditoria.objects.filter(
        ator=diretor, acao="reduzir_alocacao", motivo="ajuste de limite"
    ).exists()


def test_alocacao_para_turma_de_outro_tenant_e_recusada(instituicao, diretor):
    outra = Instituicao.objects.create(nome="Outra", documento="00.000.000/0001-02")
    turma = Turma.objects.create(instituicao=outra, nome="Turma externa")

    with pytest.raises(AlocacaoForaDaInstituicaoError):
        alocar(
            instituicao=instituicao,
            destino_turma_id=turma.id,
            quantidade=Decimal("2"),
            motivo="nao pode atravessar tenant",
            criado_por=diretor,
        )
