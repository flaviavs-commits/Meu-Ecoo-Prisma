import uuid

from django.db import models

from .normalizacao import nome_seguro


def caminho_arquivo(instance, nome):
    return f"midia/{instance.instituicao_id}/{instance.identificador}/{nome_seguro(nome)}"


class Arquivo(models.Model):
    identificador = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    instituicao = models.ForeignKey(
        "contas.Instituicao", on_delete=models.PROTECT, related_name="arquivos"
    )
    enviado_por = models.ForeignKey(
        "contas.Usuario", on_delete=models.PROTECT, related_name="arquivos_enviados"
    )
    nome_original = models.CharField(max_length=255)
    arquivo = models.FileField(upload_to=caminho_arquivo)
    tipo_mime = models.CharField(max_length=120)
    tamanho_bytes = models.PositiveBigIntegerField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em", "-id"]
        indexes = [models.Index(fields=["instituicao", "criado_em"])]
