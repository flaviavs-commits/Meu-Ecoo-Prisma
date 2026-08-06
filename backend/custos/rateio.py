"""Custo de uma chamada, na mesma unidade, venha ela de qual fornecedor vier.

Este módulo existe para responder uma pergunta só: **quanto custou esta
chamada, em dólar?** — de um jeito que a resposta signifique a mesma coisa
para o OpenRouter (cobrado por token) e para uma assinatura do Claude ou do
GPT/Codex (custo marginal zero, capacidade limitada).

A resposta alimenta `ia/conversao.py`, que converte dólar em percentual, e é o
percentual que o usuário lê. Como a conversão é a mesma para todos, **trocar de
fornecedor não interrompe a contagem nem muda a escala da conta** — muda só a
velocidade com que ela consome, que é exatamente o que se quer: uma chamada
cara no OpenRouter deve pesar mais do que a fatia de uma mensalidade já paga.

O que este módulo **não** faz: reescrever consumo passado. O percentual é
gravado no débito (`ConsumoIA`, append-only) e nunca recalculado. Recalibrar um
contrato muda o preço das chamadas seguintes, jamais o das anteriores — a
camada de provedor não é fonte de verdade da porcentagem do usuário.
"""
from decimal import Decimal

from .catalogo import contrato_do_fornecedor, tarifa_de_referencia, tarifa_do_modelo
from .modalidades import Modalidade


def custo_da_chamada(*, fornecedor, modelo, tokens_entrada, tokens_saida, custo_reportado=None):
    """Custo em dólar desta chamada, segundo o contrato do fornecedor.

    `custo_reportado` é o valor que o próprio provedor devolveu, quando devolve.
    Ele ganha do catálogo em contrato por token: é o número real cobrado, e o
    catálogo é só a nossa estimativa dele.
    """
    contrato = contrato_do_fornecedor(fornecedor)
    if contrato is None:
        # Fornecedor fora do catálogo: cai no que o provedor reportou. Sem isto,
        # ligar um fornecedor novo antes de cadastrá-lo zeraria a contagem em
        # silêncio - e conta sem contagem é conta sem limite.
        return _positivo(custo_reportado)

    # Numa assinatura o custo reportado é zero e é ignorado de propósito:
    # aceitá-lo faria a conta usar de graça justamente onde a capacidade é
    # escassa. O que ela consome é uma fatia da mensalidade já paga.
    if contrato.modalidade == Modalidade.ASSINATURA_RELATIVA:
        return _custo_relativo(
            contrato, tokens_entrada=tokens_entrada, tokens_saida=tokens_saida
        )
    if contrato.modalidade == Modalidade.ASSINATURA_RATEIO:
        return contrato.custo_por_chamada

    reportado = _positivo(custo_reportado)
    if reportado > 0:
        return reportado
    tarifa = tarifa_do_modelo(modelo)
    if tarifa is None:
        return Decimal("0")
    return tarifa.custo(tokens_entrada=tokens_entrada, tokens_saida=tokens_saida)


def _custo_relativo(contrato, *, tokens_entrada, tokens_saida):
    """O que esta chamada custaria na referência, multiplicado pelo fator.

    Ancorar no fornecedor por token, e não num valor absoluto, é o que faz o
    peso da assinatura acompanhar sozinho o tamanho da chamada e sobreviver a
    mudança de preço de mercado: se a referência encarece, a assinatura
    encarece na mesma proporção, sem ninguém reescrever número nenhum.
    """
    referencia = tarifa_de_referencia()
    if referencia is None:
        return Decimal("0")
    equivalente = referencia.custo(
        tokens_entrada=tokens_entrada, tokens_saida=tokens_saida
    )
    return equivalente * Decimal(contrato.fator_sobre_referencia)


def _positivo(valor):
    if valor is None:
        return Decimal("0")
    valor = Decimal(valor)
    return valor if valor > 0 else Decimal("0")
