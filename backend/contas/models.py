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
    ADMINISTRADOR = "ADMINISTRADOR", "Administrador Prisma"
    PROVIDER = "PROVIDER", "Provider Vitis Souls"


# Perfis da equipe: nao pertencem a uma instituicao-cliente e por isso nao
# entram no isolamento por `instituicao_id` que rege os demais.
PERFIS_INTERNOS = frozenset({Perfil.ADMINISTRADOR, Perfil.PROVIDER})


class TipoInstituicao(models.TextChoices):
    ESCOLA = "ESCOLA", "Escola"
    PRISMA = "PRISMA", "Prisma (staff interno)"
    PROVEDORA = "PROVEDORA", "Provedora"


CODIGO_PROVEDORA = "VITIS_SOULS"
CODIGO_PRISMA = "PRISMA"

# Nao sao instituicao-cliente: nao contratam plano e nao hospedam conta
# academica. Cada tipo interno aceita exatamente um perfil interno.
PERFIL_POR_TIPO_INTERNO = {
    TipoInstituicao.PROVEDORA: Perfil.PROVIDER,
    TipoInstituicao.PRISMA: Perfil.ADMINISTRADOR,
}
TIPOS_INTERNOS = frozenset(PERFIL_POR_TIPO_INTERNO)
CODIGO_POR_TIPO_INTERNO = {
    TipoInstituicao.PROVEDORA: CODIGO_PROVEDORA,
    TipoInstituicao.PRISMA: CODIGO_PRISMA,
}


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
        # Cada tipo interno tem um unico registro reservado, identificado pelo
        # codigo: e o que impede uma escola-cliente de se passar por equipe.
        codigo_reservado = CODIGO_POR_TIPO_INTERNO.get(self.tipo)
        if codigo_reservado and self.codigo != codigo_reservado:
            raise ValidationError(
                {"codigo": f"A instituição interna do tipo {self.tipo} usa o código {codigo_reservado}."}
            )

    @property
    def eh_interna(self):
        """Instituição da equipe (Vitis Souls ou Prisma), não instituição-cliente."""
        return self.tipo in TIPOS_INTERNOS

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
                    "tipo": TipoInstituicao.PROVEDORA,
                    "documento": None,
                },
            )
            extra_fields["instituicao"] = instituicao
        if instituicao.tipo != TipoInstituicao.PROVEDORA or instituicao.codigo != "VITIS_SOULS":
            raise ValueError("Superusuario precisa pertencer à Vitis Souls.")
        extra_fields.setdefault("perfil", Perfil.PROVIDER)
        if extra_fields["perfil"] != Perfil.PROVIDER:
            raise ValueError("Superusuario precisa usar o perfil PROVIDER.")
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    instituicao = models.ForeignKey(
        Instituicao, on_delete=models.PROTECT, related_name="usuarios",
        null=True, blank=True
    )
    username = None
    email = models.EmailField(unique=True)
    perfil = models.CharField(max_length=20, choices=Perfil.choices, null=True, blank=True)
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
            self.perfil == Perfil.PROVIDER
            and instituicao
            and instituicao.codigo == "VITIS_SOULS"
            and instituicao.tipo == TipoInstituicao.PROVEDORA
        ):
            raise ValidationError("Superusuario precisa ser um provider da Vitis Souls.")
        # Cada instituicao interna hospeda so o seu perfil: Vitis Souls guarda o
        # PROVIDER (acesso irrestrito) e Prisma guarda o ADMINISTRADOR (staff
        # de operacao, sem superusuario).
        if instituicao and instituicao.tipo in TIPOS_INTERNOS:
            esperado = PERFIL_POR_TIPO_INTERNO[instituicao.tipo]
            if self.perfil != esperado:
                raise ValidationError(
                    f"A instituição {instituicao.nome} só aceita contas de perfil {esperado}."
                )
        elif self.perfil in PERFIS_INTERNOS:
            raise ValidationError("Perfil da equipe exige uma instituição interna.")
        if self.perfil == Perfil.ADMINISTRADOR and self.is_superuser:
            raise ValidationError(
                "O ADMINISTRADOR é staff de operação, não superadmin: use PROVIDER."
            )

    @property
    def eh_provider(self):
        return bool(
            self.ativo
            and self.is_active
            and self.is_superuser
            and self.perfil == Perfil.PROVIDER
            and self.instituicao_id
            and self.instituicao.codigo == CODIGO_PROVEDORA
            and self.instituicao.tipo == TipoInstituicao.PROVEDORA
        )

    @property
    def eh_administrador(self):
        """Staff interno da Prisma: opera sobre usuario e monitoramento.

        Diferente do provider em profundidade, nao em alcance: enxerga as
        instituicoes-cliente, mas nao carrega `is_superuser` nem escreve nas
        entidades de dominio (turmas, conteudo, creditos, planos).
        """
        return bool(
            self.ativo
            and self.is_active
            and not self.is_superuser
            and self.perfil == Perfil.ADMINISTRADOR
            and self.instituicao_id
            and self.instituicao.codigo == CODIGO_PRISMA
            and self.instituicao.tipo == TipoInstituicao.PRISMA
        )

    @property
    def eh_staff_interno(self):
        """Pertence a equipe da Vitis Souls, em qualquer um dos dois tiers."""
        return self.eh_provider or self.eh_administrador


from .convites import ConviteProfessor


__all__ = [
    "CODIGO_PROVEDORA",
    "CODIGO_PRISMA",
    "ConviteProfessor",
    "Instituicao",
    "ModeloDaInstituicao",
    "PERFIS_INTERNOS",
    "PERFIL_POR_TIPO_INTERNO",
    "Perfil",
    "TIPOS_INTERNOS",
    "TipoInstituicao",
    "Usuario",
]

from .auditoria import RegistroDeAuditoria
