from datetime import date

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from .escopo import ModeloDaInstituicao


class Perfil(models.TextChoices):
    ALUNO = "ALUNO", "Aluno"
    PROFESSOR = "PROFESSOR", "Professor"
    DIRETOR = "DIRETOR", "Diretor"
    MANTENEDOR = "MANTENEDOR", "Mantenedor Vitis Souls"


class TipoInstituicao(models.TextChoices):
    ESCOLA = "ESCOLA", "Escola"
    MANTENEDORA = "MANTENEDORA", "Mantenedora"


class Instituicao(models.Model):
    nome = models.CharField(max_length=200)
    codigo = models.CharField(max_length=32, unique=True, null=True, blank=True)
    documento = models.CharField(max_length=18, unique=True, null=True, blank=True)
    tipo = models.CharField(
        max_length=12,
        choices=TipoInstituicao.choices,
        default=TipoInstituicao.ESCOLA,
    )
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.tipo == TipoInstituicao.ESCOLA and not self.documento:
            raise ValidationError({"documento": "Escolas precisam de documento."})
        if self.tipo == TipoInstituicao.MANTENEDORA and self.codigo != "VITIS_SOULS":
            raise ValidationError({"codigo": "A mantenedora reservada do sistema é Vitis Souls."})

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
        instituicao = extra_fields.get("instituicao")
        if instituicao is None:
            instituicao, _ = Instituicao.objects.get_or_create(
                codigo="VITIS_SOULS",
                defaults={
                    "nome": "Vitis Souls",
                    "tipo": TipoInstituicao.MANTENEDORA,
                    "documento": None,
                },
            )
            extra_fields["instituicao"] = instituicao
        if instituicao.tipo != TipoInstituicao.MANTENEDORA or instituicao.codigo != "VITIS_SOULS":
            raise ValueError("Superusuario precisa pertencer à Vitis Souls.")
        extra_fields.setdefault("perfil", Perfil.MANTENEDOR)
        if extra_fields["perfil"] != Perfil.MANTENEDOR:
            raise ValueError("Superusuario precisa usar o perfil MANTENEDOR.")
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

    def clean(self):
        super().clean()
        instituicao = self.instituicao if self.instituicao_id else None
        if self.is_superuser and not (
            self.perfil == Perfil.MANTENEDOR
            and instituicao
            and instituicao.codigo == "VITIS_SOULS"
            and instituicao.tipo == TipoInstituicao.MANTENEDORA
        ):
            raise ValidationError("Superusuarios precisam ser mantenedores da Vitis Souls.")
        if instituicao and instituicao.tipo == TipoInstituicao.MANTENEDORA and not (
            self.is_superuser and self.perfil == Perfil.MANTENEDOR
        ):
            raise ValidationError("A Vitis Souls só pode ter contas mantenedoras.")

    @property
    def eh_mantenedor(self):
        return bool(
            self.ativo
            and self.is_active
            and self.is_superuser
            and self.perfil == Perfil.MANTENEDOR
            and self.instituicao_id
            and self.instituicao.codigo == "VITIS_SOULS"
            and self.instituicao.tipo == TipoInstituicao.MANTENEDORA
        )


from .convites import ConviteProfessor


__all__ = [
    "ConviteProfessor",
    "Instituicao",
    "ModeloDaInstituicao",
    "Perfil",
    "TipoInstituicao",
    "Usuario",
]

from .auditoria import RegistroDeAuditoria
