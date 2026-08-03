from django.conf import settings
from django.db import models


class RegistroDeAuditoria(models.Model):
    ator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    acao = models.CharField(max_length=120)
    objeto_tipo = models.CharField(max_length=120)
    objeto_id = models.CharField(max_length=80)
    motivo = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
