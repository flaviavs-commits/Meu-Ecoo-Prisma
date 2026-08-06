"""Renomeia o tier MANTENEDOR para PROVIDER e cria a instituicao interna Prisma.

Duas mudancas de nomenclatura e uma de hierarquia, no mesmo passo porque as
tres tocam as mesmas duas colunas:

1. `Perfil.MANTENEDOR` -> `Perfil.PROVIDER` e `TipoInstituicao.MANTENEDORA` ->
   `PROVEDORA`. So o rotulo mudou; quem era superadmin continua superadmin.
2. Nasce `TipoInstituicao.PRISMA`, a instituicao interna que hospeda o novo
   perfil `ADMINISTRADOR` (staff de operacao, sem `is_superuser`).
3. A instituicao "Prisma" que ja existia como ESCOLA e promovida a esse tipo.
   As contas academicas que moravam nela vao para uma escola de testes, porque
   instituicao interna nao hospeda aluno, professor nem diretor.
"""
from django.db import migrations, models


NOME_ESCOLA_DE_TESTES = "Escola de Testes Prisma"
DOCUMENTO_ESCOLA_DE_TESTES = "00000000000191"
PERFIS_ACADEMICOS = ("ALUNO", "PROFESSOR", "DIRETOR")


def renomear_para_provider(apps, schema_editor):
    Instituicao = apps.get_model("contas", "Instituicao")
    Usuario = apps.get_model("contas", "Usuario")
    Instituicao.objects.filter(tipo="MANTENEDORA").update(tipo="PROVEDORA")
    Usuario.objects.filter(perfil="MANTENEDOR").update(perfil="PROVIDER")


def desfazer_renomeacao(apps, schema_editor):
    Instituicao = apps.get_model("contas", "Instituicao")
    Usuario = apps.get_model("contas", "Usuario")
    Instituicao.objects.filter(tipo="PROVEDORA").update(tipo="MANTENEDORA")
    Usuario.objects.filter(perfil="PROVIDER").update(perfil="MANTENEDOR")


def promover_instituicao_prisma(apps, schema_editor):
    Instituicao = apps.get_model("contas", "Instituicao")
    Usuario = apps.get_model("contas", "Usuario")

    prisma = (
        Instituicao.objects.filter(codigo="PRISMA").first()
        or Instituicao.objects.filter(nome__iexact="Prisma").exclude(tipo="PROVEDORA").first()
    )
    if prisma is None:
        prisma = Instituicao.objects.create(
            nome="Prisma", codigo="PRISMA", documento=None, tipo="PRISMA", ativa=True
        )
    else:
        # `documento` e unico: a escola promovida carregava um valor de escola
        # que precisa sair para nao bloquear um cadastro futuro legitimo.
        prisma.codigo = "PRISMA"
        prisma.tipo = "PRISMA"
        prisma.documento = None
        prisma.ativa = True
        prisma.save(update_fields=["codigo", "tipo", "documento", "ativa"])

    academicos = Usuario.objects.filter(instituicao_id=prisma.pk, perfil__in=PERFIS_ACADEMICOS)
    if not academicos.exists():
        return
    escola, _ = Instituicao.objects.get_or_create(
        documento=DOCUMENTO_ESCOLA_DE_TESTES,
        defaults={"nome": NOME_ESCOLA_DE_TESTES, "tipo": "ESCOLA", "ativa": True},
    )
    academicos.update(instituicao_id=escola.pk)


def rebaixar_instituicao_prisma(apps, schema_editor):
    """Volta a Prisma para escola; nao devolve as contas, que ja estao servidas."""
    Instituicao = apps.get_model("contas", "Instituicao")
    Instituicao.objects.filter(codigo="PRISMA", tipo="PRISMA").update(tipo="ESCOLA", codigo=None)


class Migration(migrations.Migration):
    dependencies = [("contas", "0007_mantenedora_vitis_souls")]

    operations = [
        migrations.AlterField(
            model_name="instituicao",
            name="tipo",
            field=models.CharField(
                choices=[
                    ("ESCOLA", "Escola"),
                    ("PRISMA", "Prisma (staff interno)"),
                    ("PROVEDORA", "Provedora"),
                ],
                default="ESCOLA",
                max_length=12,
            ),
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
                    ("ADMINISTRADOR", "Administrador Prisma"),
                    ("PROVIDER", "Provider Vitis Souls"),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.RunPython(renomear_para_provider, desfazer_renomeacao),
        migrations.RunPython(promover_instituicao_prisma, rebaixar_instituicao_prisma),
    ]
