"""As assinaturas passam a medir por fator sobre a referencia.

O catalogo de 0002 media assinatura por rateio (mensalidade / capacidade), e o
resultado contrariava a intuicao de negocio: com aqueles numeros a assinatura
saia MAIS cara por chamada que o OpenRouter, quando na pratica uma conta Claude
Max bem diluida alimenta centenas de alunos sem comprometer o limite de
ninguem. O problema nao era a formula, era depender de duas estimativas
dificeis de acertar (quantas contas, quantas chamadas cada uma).

O modo relativo troca as duas estimativas por um numero so, direto e legivel:
"esta assinatura pesa X% do que a mesma chamada pesaria no OpenRouter".

Com os fatores iniciais, a mesma chamada de 1k entrada + 0,5k saida vale:

- OpenRouter / Deepseek V4 Flash: US$ 0,00045000 (referencia, 1x)
- Claude Sonnet por assinatura:   US$ 0,00018000 (0,40x)
- GPT Luna por assinatura:        US$ 0,00022500 (0,50x)

Ou seja: o OpenRouter consome mais rapido, e a assinatura consome devagar -
que e o comportamento esperado. **Os fatores continuam sendo estimativa** e sao
o parametro a calibrar no painel conforme o uso real.
"""
from django.db import migrations


FATORES = {"claude": "0.4000", "gpt": "0.5000"}
MODELO_DE_REFERENCIA = "deepseek-v4-flash"


def adotar_modo_relativo(apps, schema_editor):
    ContratoProvedor = apps.get_model("custos", "ContratoProvedor")
    TarifaModelo = apps.get_model("custos", "TarifaModelo")

    TarifaModelo.objects.filter(modelo=MODELO_DE_REFERENCIA).update(referencia=True)
    for fornecedor, fator in FATORES.items():
        ContratoProvedor.objects.filter(fornecedor=fornecedor).update(
            modalidade="ASSINATURA_RELATIVA", fator_sobre_referencia=fator
        )
    # Contratos de assinatura anteriores ao modo relativo continuam rateando.
    ContratoProvedor.objects.filter(modalidade="ASSINATURA").update(
        modalidade="ASSINATURA_RATEIO"
    )


def voltar_ao_rateio(apps, schema_editor):
    ContratoProvedor = apps.get_model("custos", "ContratoProvedor")
    TarifaModelo = apps.get_model("custos", "TarifaModelo")
    TarifaModelo.objects.filter(modelo=MODELO_DE_REFERENCIA).update(referencia=False)
    ContratoProvedor.objects.filter(
        modalidade__in=["ASSINATURA_RELATIVA", "ASSINATURA_RATEIO"]
    ).update(modalidade="ASSINATURA", fator_sobre_referencia=0)


class Migration(migrations.Migration):
    dependencies = [("custos", "0003_assinatura_relativa")]

    operations = [migrations.RunPython(adotar_modo_relativo, voltar_ao_rateio)]
