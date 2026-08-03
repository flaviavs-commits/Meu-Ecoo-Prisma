from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]
    operations = [
        migrations.CreateModel(
            name="Instituicao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=200)),
                ("documento", models.CharField(max_length=18, unique=True)),
                ("ativa", models.BooleanField(default=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Usuario",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions without explicitly assigning them.", verbose_name="superuser status")),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("is_staff", models.BooleanField(default=False, help_text="Designates whether the user can log into this admin site.", verbose_name="staff status")),
                ("is_active", models.BooleanField(default=True, help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.", verbose_name="active")),
                ("date_joined", models.DateTimeField(auto_now_add=True, verbose_name="date joined")),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("perfil", models.CharField(choices=[("ALUNO", "Aluno"), ("PROFESSOR", "Professor"), ("DIRETOR", "Diretor")], max_length=10)),
                ("data_nascimento", models.DateField(blank=True, null=True)),
                ("responsavel_nome", models.CharField(blank=True, max_length=200)),
                ("responsavel_contato", models.CharField(blank=True, max_length=200)),
                ("consentimento_responsavel_em", models.DateTimeField(blank=True, null=True)),
                ("ativo", models.BooleanField(default=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("instituicao", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="usuarios", to="contas.instituicao")),
                ("groups", models.ManyToManyField(blank=True, help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.", related_name="usuario_set", related_query_name="usuario", to="auth.group", verbose_name="groups")),
                ("user_permissions", models.ManyToManyField(blank=True, help_text="Specific permissions for this user.", related_name="usuario_set", related_query_name="usuario", to="auth.permission", verbose_name="user permissions")),
            ],
            options={"constraints": [models.UniqueConstraint(fields=("instituicao", "email"), name="contas_email_por_instituicao")]},
        ),
    ]
