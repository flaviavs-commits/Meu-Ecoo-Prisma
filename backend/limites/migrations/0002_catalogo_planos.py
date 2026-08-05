from decimal import Decimal

from django.db import migrations


PLANOS = (
    ("PRISMA", "Prisma", Decimal("68.97"), Decimal("100")),
    ("PRISMA_PRO", "Prisma Pro", Decimal("78.97"), Decimal("171")),
    ("PRISMA_ULTRA", "Prisma Ultra", Decimal("88.97"), Decimal("271")),
)


def criar_catalogo_e_vinculos(apps, schema_editor):
    Plano = apps.get_model("limites", "PlanoInstitucional")
    Assinatura = apps.get_model("limites", "AssinaturaInstituicao")
    Cota = apps.get_model("limites", "CotaUsuario")
    Instituicao = apps.get_model("contas", "Instituicao")
    Usuario = apps.get_model("contas", "Usuario")

    for codigo, nome, preco, limite in PLANOS:
        Plano.objects.get_or_create(
            codigo=codigo,
            defaults={
                "nome": nome,
                "preco_por_conta": preco,
                "limite_percentual_por_conta": limite,
                "ativo": True,
            },
        )
    prisma = Plano.objects.get(codigo="PRISMA")
    for instituicao in Instituicao.objects.filter(tipo="ESCOLA"):
        Assinatura.objects.get_or_create(instituicao=instituicao, defaults={"plano": prisma})
    for usuario in Usuario.objects.all():
        Cota.objects.get_or_create(usuario=usuario)


class Migration(migrations.Migration):
    dependencies = [
        ("limites", "0001_initial"),
        ("contas", "0007_mantenedora_vitis_souls"),
    ]

    operations = [migrations.RunPython(criar_catalogo_e_vinculos, migrations.RunPython.noop)]
