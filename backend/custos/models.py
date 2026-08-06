from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from .modalidades import ASSINATURAS, Modalidade


class ContratoProvedor(models.Model):
    """O que a plataforma paga a um fornecedor, e sobre o que esse valor se dilui.

    Existe um contrato por fornecedor. Ele é o que permite comparar uma chamada
    do OpenRouter com uma chamada da assinatura do Claude: os dois viram custo
    por chamada na mesma unidade (dólar), e só então viram percentual.

    Há duas formas de medir uma assinatura, e a `modalidade` diz qual vale:

    - `ASSINATURA_RELATIVA` (recomendada) usa `fator_sobre_referencia`: a
      chamada pesa uma fração do que pesaria no fornecedor cobrado por token.
      Um fator de 0,4 num Claude Max diz que a mesma conversa consome 40% do
      que consumiria via OpenRouter - é assim que uma assinatura bem diluída
      alimenta centenas de alunos sem comprometer o limite de ninguém;
    - `ASSINATURA_RATEIO` usa `contas_atendidas` e `chamadas_por_conta_no_mes`,
      estimativas que se recalibram (ver `custos/recalibracao.py`). Uma
      assinatura que atende 200 contas tem rateio por chamada maior do que a
      mesma assinatura atendendo 400.
    """

    fornecedor = models.CharField(max_length=80, unique=True)
    modalidade = models.CharField(max_length=20, choices=Modalidade.choices)
    # Só para assinatura. Em dólar, para ficar na mesma unidade do por-token.
    mensalidade = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    contas_atendidas = models.PositiveIntegerField(default=1)
    chamadas_por_conta_no_mes = models.PositiveIntegerField(default=1)
    # Só para ASSINATURA_RELATIVA: quanto esta chamada pesa comparada à mesma
    # chamada no fornecedor de referência. 0,4 = 40% do peso.
    fator_sobre_referencia = models.DecimalField(
        max_digits=6, decimal_places=4, default=0
    )
    ativo = models.BooleanField(default=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["fornecedor"]

    def __str__(self):
        return f"{self.fornecedor} ({self.modalidade})"

    def clean(self):
        if self.modalidade == Modalidade.ASSINATURA_RATEIO:
            if self.mensalidade <= 0:
                raise ValidationError({"mensalidade": "Assinatura precisa de mensalidade."})
            if not self.contas_atendidas or not self.chamadas_por_conta_no_mes:
                raise ValidationError(
                    "Rateio precisa saber por quantas contas e chamadas se divide."
                )
        if self.modalidade == Modalidade.ASSINATURA_RELATIVA and (
            self.fator_sobre_referencia <= 0
        ):
            raise ValidationError(
                {"fator_sobre_referencia": "Informe o peso da chamada sobre a referência."}
            )

    @property
    def chamadas_estimadas_no_mes(self):
        return self.contas_atendidas * self.chamadas_por_conta_no_mes

    @property
    def eh_assinatura(self):
        return self.modalidade in ASSINATURAS

    @property
    def custo_por_chamada(self):
        """Rateio da mensalidade. Zero para quem não rateia."""
        if self.modalidade != Modalidade.ASSINATURA_RATEIO:
            return Decimal("0")
        estimadas = self.chamadas_estimadas_no_mes
        if estimadas <= 0:
            return Decimal("0")
        return Decimal(self.mensalidade) / Decimal(estimadas)


class TarifaModelo(models.Model):
    """Preço por mil tokens de um modelo cobrado por token.

    Vive em contrato `POR_TOKEN`. A tarifa marcada como `referencia` tem um
    segundo papel: é a régua contra a qual as assinaturas relativas medem o
    peso das chamadas delas.
    """

    contrato = models.ForeignKey(
        ContratoProvedor, on_delete=models.CASCADE, related_name="tarifas"
    )
    modelo = models.CharField(max_length=160, unique=True)
    # A tarifa que serve de régua para as assinaturas relativas: é o "1x"
    # contra o qual os fatores são lidos.
    referencia = models.BooleanField(default=False)
    preco_por_mil_entrada = models.DecimalField(max_digits=12, decimal_places=8, default=0)
    preco_por_mil_saida = models.DecimalField(max_digits=12, decimal_places=8, default=0)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["modelo"]

    def __str__(self):
        return self.modelo

    def custo(self, *, tokens_entrada, tokens_saida):
        mil = Decimal("1000")
        return (
            Decimal(tokens_entrada) / mil * self.preco_por_mil_entrada
            + Decimal(tokens_saida) / mil * self.preco_por_mil_saida
        )
