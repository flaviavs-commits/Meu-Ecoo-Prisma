"""Passa o limite de uso a ser contado por competencia mensal.

Antes desta migracao `estado_cota` somava todo o `ConsumoIA` da conta desde
sempre. Como o plano e vendido por conta/mes, a conta que esgotasse o
percentual num mes ficaria bloqueada nos meses seguintes mesmo com a escola
sendo cobrada de novo.

O backfill deriva a competencia de `criado_em`, que era a unica informacao
temporal existente, e roda em lote para nao virar uma migracao O(n) de
round-trips num predeploy.
"""

from django.db import migrations, models


LOTE = 2000


def preencher_ciclo(apps, schema_editor):
    Consumo = apps.get_model("limites", "ConsumoIA")
    pendentes = Consumo.objects.filter(ciclo="").only("pk", "criado_em")
    lote = []
    for consumo in pendentes.iterator(chunk_size=LOTE):
        # `criado_em` e aware (USE_TZ) e TIME_ZONE e UTC; `strftime` aqui da o
        # mesmo resultado que `limites.ciclo.ciclo_de`, que nao pode ser
        # importado numa migracao (o codigo da app pode mudar depois).
        consumo.ciclo = consumo.criado_em.strftime("%Y-%m")
        lote.append(consumo)
        if len(lote) >= LOTE:
            Consumo.objects.bulk_update(lote, ["ciclo"])
            lote = []
    if lote:
        Consumo.objects.bulk_update(lote, ["ciclo"])


def limpar_ciclo(apps, schema_editor):
    apps.get_model("limites", "ConsumoIA").objects.update(ciclo="")


class Migration(migrations.Migration):
    dependencies = [("limites", "0002_catalogo_planos")]

    operations = [
        migrations.AddField(
            model_name="consumoia",
            name="ciclo",
            field=models.CharField(default="", max_length=7),
            preserve_default=False,
        ),
        migrations.RunPython(preencher_ciclo, limpar_ciclo),
        migrations.AddIndex(
            model_name="consumoia",
            index=models.Index(
                fields=["usuario", "ciclo"], name="limites_con_usuario_659a65_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="consumoia",
            index=models.Index(
                fields=["instituicao", "ciclo"], name="limites_con_institu_c12dfc_idx"
            ),
        ),
    ]
