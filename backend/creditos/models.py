from django.db import models


class TipoLancamento(models.TextChoices):
    CREDITO = "CREDITO", "Credito"
    DEBITO = "DEBITO", "Debito"
    ALOCACAO = "ALOCACAO", "Alocacao"
    ESTORNO = "ESTORNO", "Estorno"


class LancamentoImutavelError(Exception):
    """Levantada quando alguem tenta alterar ou apagar um lancamento existente."""


class Lancamento(models.Model):
    """Ledger append-only de creditos. Saldo e sempre derivado da soma, nunca uma coluna."""

    instituicao = models.ForeignKey(
        "contas.Instituicao", on_delete=models.PROTECT, related_name="lancamentos"
    )
    usuario = models.ForeignKey(
        "contas.Usuario",
        on_delete=models.PROTECT,
        related_name="lancamentos",
        null=True,
        blank=True,
    )
    turma = models.ForeignKey(
        "academico.Turma",
        on_delete=models.PROTECT,
        related_name="lancamentos",
        null=True,
        blank=True,
    )
    tipo = models.CharField(max_length=10, choices=TipoLancamento.choices)
    quantidade = models.DecimalField(max_digits=14, decimal_places=4)
    motivo = models.TextField()
    referencia = models.ForeignKey(
        "ia.ChamadaIA",
        on_delete=models.PROTECT,
        related_name="lancamentos",
        null=True,
        blank=True,
    )
    criado_por = models.ForeignKey(
        "contas.Usuario",
        on_delete=models.PROTECT,
        related_name="lancamentos_criados",
        null=True,
        blank=True,
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantidade__gt=0), name="creditos_quantidade_positiva"
            ),
            models.UniqueConstraint(
                fields=["referencia", "tipo"],
                condition=models.Q(tipo=TipoLancamento.DEBITO),
                name="creditos_debito_unico_por_referencia",
            ),
        ]
        indexes = [
            models.Index(fields=["instituicao", "usuario"]),
            models.Index(fields=["instituicao", "turma"]),
        ]

    def __str__(self) -> str:
        return f"{self.tipo} {self.quantidade} ({self.instituicao_id})"

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise LancamentoImutavelError(
                "Lancamento e append-only: corrija com o lancamento contrario, nao com UPDATE."
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise LancamentoImutavelError(
            "Lancamento e append-only: nunca e apagado, nem por engano."
        )


class TravaSaldoUsuario(models.Model):
    """Linha de controle so para dar `select_for_update`: o saldo em si nunca mora aqui.

    Lancamento nao tem coluna estavel para travar quando o usuario ainda nao
    tem nenhum lancamento - por isso existe uma linha por usuario, criada sob
    demanda, so para serializar autorizacao e debito concorrentes.
    """

    usuario = models.OneToOneField(
        "contas.Usuario", on_delete=models.CASCADE, related_name="trava_saldo_creditos"
    )

    def __str__(self) -> str:
        return f"trava usuario {self.usuario_id}"


class ConfiguracaoAlertaSaldo(models.Model):
    """Limiar por instituicao para o alerta de saldo baixo (secao 5.7)."""

    instituicao = models.OneToOneField(
        "contas.Instituicao", on_delete=models.CASCADE, related_name="config_alerta_creditos"
    )
    limiar = models.DecimalField(max_digits=14, decimal_places=4)

    def __str__(self) -> str:
        return f"limiar {self.limiar} ({self.instituicao_id})"
