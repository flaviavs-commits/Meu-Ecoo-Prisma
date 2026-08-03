from django.db import models


class ModeloDaInstituicao(models.Model):
    instituicao = models.ForeignKey(
        "contas.Instituicao",
        on_delete=models.PROTECT,
        db_index=True,
    )

    class Meta:
        abstract = True


class QuerySetDaInstituicao(models.QuerySet):
    def da_instituicao(self, instituicao):
        return self.filter(instituicao=instituicao)


class ManagerDaInstituicao(models.Manager.from_queryset(QuerySetDaInstituicao)):
    pass
