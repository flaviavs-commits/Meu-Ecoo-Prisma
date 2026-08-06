from django.db import models


class Modalidade(models.TextChoices):
    """Como o custo de uma chamada é apurado para cada fornecedor.

    `POR_TOKEN` tem custo marginal real: a chamada custa o que consumiu.

    As duas de assinatura existem porque assinatura tem custo marginal zero e
    capacidade limitada — o que a chamada consome não é dinheiro novo, é uma
    fatia de mensalidade já paga. Muda só o jeito de medir essa fatia:

    - `ASSINATURA_RATEIO` divide a mensalidade pela capacidade estimada. É o
      número economicamente "verdadeiro", mas depende de duas estimativas
      difíceis de saber (quantas contas, quantas chamadas cada uma).
    - `ASSINATURA_RELATIVA` mede a chamada **em relação ao que ela custaria no
      fornecedor de referência** (o cobrado por token) e aplica um fator. Um
      fator de 0,4 diz "esta chamada pesa 40% do que pesaria no OpenRouter".
      É a modalidade recomendada: um número só, direto, que sobrevive a
      mudança de preço do fornecedor e escala sozinho com o tamanho da chamada.
    """

    POR_TOKEN = "POR_TOKEN", "Cobrado por token"
    ASSINATURA_RATEIO = "ASSINATURA_RATEIO", "Assinatura — rateio da mensalidade"
    ASSINATURA_RELATIVA = "ASSINATURA_RELATIVA", "Assinatura — fator sobre a referência"


ASSINATURAS = frozenset(
    {Modalidade.ASSINATURA_RATEIO, Modalidade.ASSINATURA_RELATIVA}
)
