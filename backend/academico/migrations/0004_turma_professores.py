"""Uma turma passa a ter N professores, nao apenas o titular.

O canvas do Sistema Prisma descreve "cada turma pode ter N professores e cada
professor pode lecionar em N turmas". O `professor_responsavel` continua onde
estava, agora como titular da turma, e o corpo docente vira uma relacao
muitos-para-muitos. O backfill matricula o titular atual como professor, para
que nenhuma turma existente perca o professor que ja tinha.
"""
from django.db import migrations, models


def matricular_titulares_como_professores(apps, schema_editor):
    Turma = apps.get_model("academico", "Turma")
    for turma in Turma.objects.exclude(professor_responsavel_id=None).iterator():
        turma.professores.add(turma.professor_responsavel_id)


def esvaziar_corpo_docente(apps, schema_editor):
    Turma = apps.get_model("academico", "Turma")
    for turma in Turma.objects.iterator():
        turma.professores.clear()


class Migration(migrations.Migration):
    dependencies = [
        ("academico", "0003_notas_existentes_oficiais"),
        ("contas", "0008_provider_e_instituicao_prisma"),
    ]

    operations = [
        migrations.AddField(
            model_name="turma",
            name="professores",
            field=models.ManyToManyField(
                blank=True, related_name="turmas_lecionadas", to="contas.usuario"
            ),
        ),
        migrations.RunPython(
            matricular_titulares_como_professores, esvaziar_corpo_docente
        ),
    ]
