from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):
    dependencies = [("contas", "0002_alter_usuario_managers_and_more")]

    operations = [
        migrations.AddField(
            model_name="usuario",
            name="criado_em",
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="usuario",
            name="atualizado_em",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
