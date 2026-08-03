from datetime import timedelta
import hashlib
import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone


class ConviteProfessor(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        ACEITO = "ACEITO", "Aceito"
        EXPIRADO = "EXPIRADO", "Expirado"

    instituicao = models.ForeignKey(
        "contas.Instituicao", on_delete=models.PROTECT, related_name="convites_professor"
    )
    email = models.EmailField()
    convidado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="convites_enviados"
    )
    token_hash = models.CharField(max_length=64, unique=True)
    expira_em = models.DateTimeField()
    aceito_em = models.DateTimeField(null=True, blank=True)
    envio_email_status = models.CharField(max_length=20, default="PENDENTE")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["instituicao", "email"],
                condition=models.Q(aceito_em__isnull=True),
                name="contas_convite_pendente_unico",
            )
        ]

    @property
    def status(self):
        if self.aceito_em:
            return self.Status.ACEITO
        if self.expira_em <= timezone.now():
            return self.Status.EXPIRADO
        return self.Status.PENDENTE

    def __str__(self):
        return f"{self.email} ({self.status})"


def convite_professor(*, instituicao, email, convidado_por, adaptador=None):
    from .email import AdaptadorEmailConvite

    if convidado_por.instituicao_id != instituicao.id or convidado_por.perfil != "DIRETOR":
        raise ValueError("Somente o diretor da instituicao pode convidar professores.")
    if not instituicao.ativa:
        raise ValueError("Instituicao inativa nao pode receber convites.")
    token = secrets.token_urlsafe(32)
    convite = ConviteProfessor.objects.create(
        instituicao=instituicao,
        email=email,
        convidado_por=convidado_por,
        token_hash=hashlib.sha256(token.encode("utf-8")).hexdigest(),
        expira_em=timezone.now() + timedelta(days=7),
    )
    (adaptador or AdaptadorEmailConvite()).enviar(convite=convite, token=token)
    return convite
