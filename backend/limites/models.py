from decimal import Decimal

from django.db import models

from .ciclo import TAMANHO as CICLO_TAMANHO


# O limite do plano pode ser 171% ou 271%; o teto abaixo representa apenas o
# maior valor que cabe no campo de consumo, não o limite comercial da conta.
PERCENTUAL_MAXIMO = Decimal("9999999.9999")


class CodigoPlano(models.TextChoices):
    PRISMA = "PRISMA", "Prisma"
    PRISMA_PRO = "PRISMA_PRO", "Prisma Pro"
    PRISMA_ULTRA = "PRISMA_ULTRA", "Prisma Ultra"


class Periodicidade(models.TextChoices):
    """Intervalo de cobranca da assinatura, contratado pela instituicao.

    Nao confundir com o ciclo de `limites/ciclo.py`, que e sempre mensal: aquele
    e a janela de apuracao do consumo, este e o intervalo em que a escola paga.
    Uma assinatura anual continua tendo doze janelas mensais de uso.
    """

    MENSAL = "MENSAL", "Mensal"
    ANUAL = "ANUAL", "Anual"


class CotaImutavelError(Exception):
    """Levantada quando um consumo registrado seria alterado ou apagado."""


class CotaUsuario(models.Model):
    """Linha de controle usada para serializar o uso de uma conta."""

    usuario = models.OneToOneField(
        "contas.Usuario",
        on_delete=models.CASCADE,
        related_name="cota_ia",
    )
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)


class PlanoInstitucional(models.Model):
    """Catalogo de planos vendidos por conta para cada instituicao."""

    codigo = models.CharField(max_length=16, choices=CodigoPlano.choices, unique=True)
    nome = models.CharField(max_length=80)
    preco_por_conta = models.DecimalField(max_digits=10, decimal_places=2)
    limite_percentual_por_conta = models.DecimalField(max_digits=8, decimal_places=4)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["preco_por_conta", "id"]


class AssinaturaInstituicao(models.Model):
    """Plano atualmente contratado por uma instituicao escolar."""

    instituicao = models.OneToOneField(
        "contas.Instituicao",
        on_delete=models.CASCADE,
        related_name="assinatura_prisma",
    )
    plano = models.ForeignKey(
        PlanoInstitucional,
        on_delete=models.PROTECT,
        related_name="assinaturas",
    )
    periodicidade = models.CharField(
        max_length=6,
        choices=Periodicidade.choices,
        default=Periodicidade.MENSAL,
    )
    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)


class ConsumoIA(models.Model):
    """Registro append-only do percentual debitado por uma chamada concluída."""

    usuario = models.ForeignKey(
        "contas.Usuario", on_delete=models.PROTECT, related_name="consumos_ia"
    )
    instituicao = models.ForeignKey(
        "contas.Instituicao", on_delete=models.PROTECT, related_name="consumos_ia"
    )
    referencia = models.OneToOneField(
        "ia.ChamadaIA",
        on_delete=models.PROTECT,
        related_name="consumo_percentual",
    )
    fornecedor = models.CharField(max_length=80)
    modelo = models.CharField(max_length=160)
    classe_tarefa = models.CharField(max_length=20)
    # Competencia (`YYYY-MM`) em que este consumo entra no limite do plano.
    # Gravada no debito e nunca recalculada: ver `limites/ciclo.py`.
    ciclo = models.CharField(max_length=CICLO_TAMANHO)
    percentual = models.DecimalField(max_digits=7, decimal_places=4)
    custo_bruto = models.DecimalField(max_digits=14, decimal_places=8, default=0)
    metadados = models.JSONField(default=dict, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(percentual__gt=0),
                name="limites_consumo_percentual_valido",
            )
        ]
        indexes = [
            # Consulta quente: somar o consumo da conta na competencia aberta.
            models.Index(fields=["usuario", "ciclo"]),
            models.Index(fields=["instituicao", "ciclo"]),
            models.Index(fields=["instituicao", "usuario", "criado_em"]),
            models.Index(fields=["fornecedor", "modelo", "criado_em"]),
        ]

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise CotaImutavelError(
                "Consumo de IA e append-only: corrija por estorno auditado, nao por UPDATE."
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise CotaImutavelError("Consumo de IA nao pode ser apagado.")
