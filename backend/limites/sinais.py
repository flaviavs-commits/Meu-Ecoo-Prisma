from django.db.models.signals import post_save
from django.dispatch import receiver

from contas.models import Usuario

from .models import CotaUsuario


@receiver(post_save, sender=Usuario)
def criar_cota_para_conta(sender, instance, created, **kwargs):
    if created:
        CotaUsuario.objects.get_or_create(usuario=instance)
