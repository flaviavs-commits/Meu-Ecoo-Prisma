"""Preserva a visibilidade das notas que ja existiam antes da aprovacao.

Em 2026-08-05 `consultar_notas` passou a mostrar ao diretor apenas nota com
`oficial=True`, e `aprovar_nota` virou a unica porta para esse estado. Como
`oficial` nasceu `default=False` e nada antes deste dia setava o campo, toda
nota ja lancada ficaria invisivel ao diretor no deploy - uma perda funcional
silenciosa, sem erro na tela, ate cada professor reaprovar nota por nota.

Estas notas ja eram visiveis ao diretor sob a regra anterior, entao marca-las
como aprovadas mantem o comportamento observado e nao concede nada novo: a
regra nova vale para tudo que for lancado a partir daqui.

Sem reversao automatica: depois do backfill nao ha como distinguir a nota
marcada aqui da nota aprovada de verdade por um professor, e adivinhar
esconderia nota legitima do diretor. Reverter, se preciso, e uma decisao
manual com criterio de data (`criado_em` anterior ao deploy).
"""

from django.db import migrations


def marcar_notas_anteriores_como_oficiais(apps, schema_editor):
    Nota = apps.get_model("academico", "Nota")
    Nota.objects.filter(oficial=False).update(oficial=True)


class Migration(migrations.Migration):
    dependencies = [
        ("academico", "0002_turma_professor_responsavel_configuracaonota_and_more"),
    ]

    operations = [
        migrations.RunPython(
            marcar_notas_anteriores_como_oficiais, migrations.RunPython.noop
        )
    ]
