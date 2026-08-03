from django.db import models


class Turma(models.Model):
    instituicao = models.ForeignKey("contas.Instituicao", on_delete=models.PROTECT, related_name="turmas")
    nome = models.CharField(max_length=120, default="Turma")
