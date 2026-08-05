from django.db import models


class StatusAgenda(models.TextChoices):
    PENDENTE = "PENDENTE", "Pendente"
    CONCLUIDA = "CONCLUIDA", "Concluida"
    CANCELADA = "CANCELADA", "Cancelada"


class AgendaEstudo(models.Model):
    aluno = models.ForeignKey(
        "contas.Usuario", on_delete=models.CASCADE, related_name="agenda_estudos"
    )
    instituicao = models.ForeignKey(
        "contas.Instituicao", on_delete=models.PROTECT, related_name="agendas_estudo"
    )
    titulo = models.CharField(max_length=200)
    disciplina = models.CharField(max_length=120, blank=True)
    descricao = models.TextField(blank=True)
    agendado_para = models.DateTimeField()
    status = models.CharField(
        max_length=10, choices=StatusAgenda.choices, default=StatusAgenda.PENDENTE
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["agendado_para", "id"]
        indexes = [models.Index(fields=["aluno", "status", "agendado_para"])]
