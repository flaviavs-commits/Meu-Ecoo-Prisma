from django.contrib import admin

from .models import ChamadaIA


@admin.register(ChamadaIA)
class ChamadaIAAdmin(admin.ModelAdmin):
    list_display = (
        "criada_em", "instituicao", "usuario", "classe_tarefa", "modelo", "status",
        "tokens_entrada", "tokens_saida", "creditos_debitados", "erro_codigo",
    )
    search_fields = ("instituicao__nome", "usuario__email", "modelo", "erro_codigo")
    list_filter = ("classe_tarefa", "status", "instituicao", "criada_em")
    raw_id_fields = ("instituicao", "usuario")
    readonly_fields = tuple(field.name for field in ChamadaIA._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
