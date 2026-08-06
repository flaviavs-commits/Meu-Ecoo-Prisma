"""Catalogo inicial dos tres fornecedores em uso.

Os numeros abaixo sao **ponto de partida operacional, nao verdade contabil**:
mensalidade e preco por token mudam, e a estimativa de quantas contas cada
assinatura atende e justamente o que se recalibra depois
(`custos/recalibracao.py`). Estao aqui para que o sistema nasca medindo em vez
de nascer com custo zero - o painel corrige daqui para frente.

A conta que importa e a diferenca de peso entre eles. Com os valores iniciais:

- OpenRouter / Deepseek V4 Flash: ~US$ 0,00045 numa chamada de 1k entrada +
  0,5k saida - custo real, cobrado por token;
- Claude Sonnet por assinatura: US$ 100 / (200 contas x 300 chamadas) =
  US$ 0,00167 por chamada;
- GPT Luna por assinatura: US$ 60 / (150 contas x 300 chamadas) =
  US$ 0,00133 por chamada.

Ou seja: com estes numeros o OpenRouter e o mais **barato** por chamada, e nao
o mais caro. Isso e proposital - o rateio nao inventa que assinatura e sempre
melhor, ele mede. Se a mensalidade for pouco usada, a fatia por chamada fica
cara; se for bem diluida, fica barata. E o painel que mostra qual esta valendo
mais a pena.
"""
from django.db import migrations


CONTRATOS = [
    {
        "fornecedor": "openrouter",
        "modalidade": "POR_TOKEN",
        "mensalidade": "0",
        "contas_atendidas": 1,
        "chamadas_por_conta_no_mes": 1,
        "tarifas": [
            {
                "modelo": "deepseek-v4-flash",
                "preco_por_mil_entrada": "0.00020000",
                "preco_por_mil_saida": "0.00050000",
            }
        ],
    },
    {
        "fornecedor": "claude",
        "modalidade": "ASSINATURA",
        "mensalidade": "100.0000",
        "contas_atendidas": 200,
        "chamadas_por_conta_no_mes": 300,
        "tarifas": [],
    },
    {
        "fornecedor": "gpt",
        "modalidade": "ASSINATURA",
        "mensalidade": "60.0000",
        "contas_atendidas": 150,
        "chamadas_por_conta_no_mes": 300,
        "tarifas": [],
    },
]


def semear(apps, schema_editor):
    ContratoProvedor = apps.get_model("custos", "ContratoProvedor")
    TarifaModelo = apps.get_model("custos", "TarifaModelo")
    for dados in CONTRATOS:
        tarifas = dados.pop("tarifas")
        contrato, _ = ContratoProvedor.objects.get_or_create(
            fornecedor=dados["fornecedor"], defaults=dados
        )
        for tarifa in tarifas:
            TarifaModelo.objects.get_or_create(
                modelo=tarifa["modelo"], defaults={**tarifa, "contrato": contrato}
            )


def limpar(apps, schema_editor):
    ContratoProvedor = apps.get_model("custos", "ContratoProvedor")
    ContratoProvedor.objects.filter(
        fornecedor__in=[dados["fornecedor"] for dados in CONTRATOS]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("custos", "0001_initial")]

    operations = [migrations.RunPython(semear, limpar)]
