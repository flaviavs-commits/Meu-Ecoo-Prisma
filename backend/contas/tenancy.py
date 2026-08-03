"""Primitivas explicitas de isolamento por instituicao."""

from django.db import models


class QuerySetDaInstituicao(models.QuerySet):
    def da_instituicao(self, instituicao):
        return self.filter(instituicao=instituicao)


class ManagerDaInstituicao(models.Manager.from_queryset(QuerySetDaInstituicao)):
    def da_instituicao(self, instituicao):
        return self.get_queryset().da_instituicao(instituicao)


class ModeloDaInstituicao(models.Model):
    instituicao = models.ForeignKey(
        "contas.Instituicao", on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_set", db_index=True
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    objects = ManagerDaInstituicao()

    class Meta:
        abstract = True
