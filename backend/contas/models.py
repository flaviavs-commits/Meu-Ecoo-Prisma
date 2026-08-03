from datetime import date

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from .escopo import ModeloDaInstituicao


class Perfil(models.TextChoices):
    ALUNO = "ALUNO", "Aluno"
    PROFESSOR = "PROFESSOR", "Professor"
    DIRETOR = "DIRETOR", "Diretor"


class Instituicao(models.Model):
    nome = models.CharField(max_length=200)
    documento = models.CharField(max_length=18, unique=True)
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def da_instituicao(self, instituicao):
        return self.get_queryset().filter(instituicao=instituicao)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O e-mail e obrigatorio.")
        usuario = self.model(email=self.normalize_email(email), **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if not extra_fields["is_staff"] or not extra_fields["is_superuser"]:
            raise ValueError("Superusuario precisa de is_staff e is_superuser.")
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    instituicao = models.ForeignKey(
        Instituicao, on_delete=models.PROTECT, related_name="usuarios",
        null=True, blank=True
    )
    username = None
    email = models.EmailField(unique=True)
    perfil = models.CharField(max_length=10, choices=Perfil.choices, null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    responsavel_nome = models.CharField(max_length=200, blank=True)
    responsavel_contato = models.CharField(max_length=200, blank=True)
    consentimento_responsavel_em = models.DateTimeField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UsuarioManager()

    @property
    def e_menor(self):
        if not self.data_nascimento:
            return False
        hoje = date.today()
        idade = hoje.year - self.data_nascimento.year
        if (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day):
            idade -= 1
        return idade < 18


__all__ = ["Instituicao", "ModeloDaInstituicao", "Perfil", "Usuario"]

from .auditoria import RegistroDeAuditoria
