from django.db import migrations, models


def criar_mantenedora_vitis_souls(apps, schema_editor):
    Instituicao = apps.get_model("contas", "Instituicao")
    Usuario = apps.get_model("contas", "Usuario")
    vitis, _ = Instituicao.objects.get_or_create(
        codigo="VITIS_SOULS",
        defaults={
            "nome": "Vitis Souls",
            "documento": None,
            "tipo": "MANTENEDORA",
            "ativa": True,
        },
    )
    Usuario.objects.filter(is_superuser=True).update(
        instituicao_id=vitis.pk,
        perfil="MANTENEDOR",
    )


class Migration(migrations.Migration):
    dependencies = [("contas", "0006_conviteprofessor")]

    operations = [
        migrations.AddField(
            model_name="instituicao",
            name="codigo",
            field=models.CharField(blank=True, max_length=32, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="instituicao",
            name="tipo",
            field=models.CharField(
                choices=[("ESCOLA", "Escola"), ("MANTENEDORA", "Mantenedora")],
                default="ESCOLA",
                max_length=12,
            ),
        ),
        migrations.AlterField(
            model_name="instituicao",
            name="documento",
            field=models.CharField(blank=True, max_length=18, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="usuario",
            name="perfil",
            field=models.CharField(
                blank=True,
                choices=[
                    ("ALUNO", "Aluno"),
                    ("PROFESSOR", "Professor"),
                    ("DIRETOR", "Diretor"),
                    ("MANTENEDOR", "Mantenedor Vitis Souls"),
                ],
                max_length=10,
                null=True,
            ),
        ),
        migrations.RunPython(criar_mantenedora_vitis_souls, migrations.RunPython.noop),
    ]
