from django.contrib import admin

from .models import ConfiguracaoAlertaSaldo, Lancamento, TravaSaldoUsuario


class SomenteLeituraAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Lancamento)
class LancamentoAdmin(SomenteLeituraAdmin):
    list_display = (
        "criado_em", "instituicao", "tipo", "quantidade", "usuario", "turma", "motivo",
    )
    search_fields = ("instituicao__nome", "usuario__email", "motivo")
    list_filter = ("tipo", "instituicao", "criado_em")
    raw_id_fields = ("instituicao", "usuario", "turma", "referencia", "criado_por")
    readonly_fields = tuple(field.name for field in Lancamento._meta.fields)


@admin.register(ConfiguracaoAlertaSaldo)
class ConfiguracaoAlertaSaldoAdmin(admin.ModelAdmin):
    list_display = ("instituicao", "limiar")
    list_filter = ("instituicao",)


@admin.register(TravaSaldoUsuario)
class TravaSaldoUsuarioAdmin(SomenteLeituraAdmin):
    list_display = ("usuario",)
    search_fields = ("usuario__email",)
    raw_id_fields = ("usuario",)
