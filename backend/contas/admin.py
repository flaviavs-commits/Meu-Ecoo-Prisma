from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count

from .auditoria import RegistroDeAuditoria
from .forms import UsuarioChangeForm, UsuarioCreationForm
from .models import ConviteProfessor, Instituicao, Usuario


@admin.register(Instituicao)
class InstituicaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "documento", "ativa", "saldo", "quantidade_usuarios", "criado_em")
    search_fields = ("nome", "documento")
    list_filter = ("ativa",)
    readonly_fields = ("criado_em", "atualizado_em")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_quantidade_usuarios=Count("usuarios"))

    @admin.display(description="Usuarios")
    def quantidade_usuarios(self, obj):
        return obj._quantidade_usuarios

    @admin.display(description="Saldo de creditos")
    def saldo(self, obj):
        from creditos.saldo import saldo_instituicao

        return saldo_instituicao(obj.pk)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    form = UsuarioChangeForm
    add_form = UsuarioCreationForm
    list_display = (
        "email", "first_name", "perfil", "instituicao", "ativo", "consentimento_pendente",
    )
    search_fields = ("email", "first_name", "last_name", "instituicao__nome")
    list_filter = ("perfil", "ativo", "is_active", "instituicao")
    ordering = ("email",)
    raw_id_fields = ("instituicao",)
    fieldsets = (
        ("Identidade", {"fields": ("email", "first_name", "last_name")} ),
        ("Vinculo institucional", {"fields": ("instituicao", "perfil", "ativo")} ),
        ("Protecoes", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")} ),
        ("Dados de consentimento", {"fields": ("data_nascimento", "responsavel_nome", "responsavel_contato", "consentimento_responsavel_em")} ),
        ("Datas", {"fields": ("last_login", "date_joined", "criado_em", "atualizado_em")} ),
    )
    readonly_fields = ("last_login", "date_joined", "criado_em", "atualizado_em")
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "first_name", "instituicao", "perfil", "password1", "password2")} ),
    )

    @admin.display(boolean=True, description="Consentimento pendente")
    def consentimento_pendente(self, obj):
        return obj.e_menor and obj.consentimento_responsavel_em is None


@admin.register(ConviteProfessor)
class ConviteProfessorAdmin(admin.ModelAdmin):
    list_display = ("email", "instituicao", "status", "expira_em", "envio_email_status")
    search_fields = ("email", "instituicao__nome")
    list_filter = ("envio_email_status", "instituicao")
    readonly_fields = (
        "instituicao", "email", "convidado_por", "token_hash", "expira_em", "aceito_em",
        "envio_email_status", "criado_em",
    )
    raw_id_fields = ("convidado_por",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RegistroDeAuditoria)
class RegistroDeAuditoriaAdmin(admin.ModelAdmin):
    list_display = ("criado_em", "ator", "acao", "objeto_tipo", "objeto_id", "motivo")
    search_fields = ("acao", "objeto_tipo", "objeto_id", "motivo", "ator__email")
    list_filter = ("acao", "objeto_tipo", "ator__instituicao", "criado_em")
    readonly_fields = ("ator", "acao", "objeto_tipo", "objeto_id", "motivo", "criado_em")
    raw_id_fields = ("ator",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
