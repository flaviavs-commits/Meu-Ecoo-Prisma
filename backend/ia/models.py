from django.db import models


class ClasseTarefa(models.TextChoices):
    TUTORIA = "TUTORIA", "Tutoria"
    GERACAO = "GERACAO", "Geracao"
    CORRECAO = "CORRECAO", "Correcao"
    RESUMO = "RESUMO", "Resumo"


class StatusChamada(models.TextChoices):
    PENDENTE = "PENDENTE", "Pendente"
    SUCESSO = "SUCESSO", "Sucesso"
    ERRO = "ERRO", "Erro"


class ChamadaIA(models.Model):
    instituicao = models.ForeignKey(
        "contas.Instituicao",
        on_delete=models.PROTECT,
        related_name="chamadas_ia",
        null=True,
        blank=True,
    )
    usuario = models.ForeignKey(
        "contas.Usuario",
        on_delete=models.PROTECT,
        related_name="chamadas_ia",
        null=True,
        blank=True,
    )
    classe_tarefa = models.CharField(
        max_length=10, choices=ClasseTarefa.choices, default=ClasseTarefa.TUTORIA
    )
    fornecedor = models.CharField(max_length=80, blank=True)
    modelo = models.CharField(max_length=160, blank=True)
    tokens_entrada = models.PositiveIntegerField(default=0)
    tokens_saida = models.PositiveIntegerField(default=0)
    custo_bruto = models.DecimalField(max_digits=14, decimal_places=8, default=0)
    percentual_debitado = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    status = models.CharField(
        max_length=10, choices=StatusChamada.choices, default=StatusChamada.PENDENTE
    )
    erro_codigo = models.CharField(max_length=80, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    concluida_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["instituicao", "usuario", "status"]),
        ]
