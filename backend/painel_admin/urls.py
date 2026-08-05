from django.urls import path

from .views import (
    dashboard,
    registros,
    usuario,
    usuario_desativar,
    usuario_perfil,
    usuario_zerar_creditos,
    usuarios,
)


urlpatterns = [
    path("", dashboard, name="painel-dashboard"),
    path("usuarios/", usuarios, name="painel-usuarios"),
    path("usuarios/<int:pk>/", usuario, name="painel-usuario"),
    path("usuarios/<int:pk>/perfil/", usuario_perfil, name="painel-usuario-perfil"),
    path("usuarios/<int:pk>/desativar/", usuario_desativar, name="painel-usuario-desativar"),
    path(
        "usuarios/<int:pk>/zerar-creditos/",
        usuario_zerar_creditos,
        name="painel-usuario-zerar-creditos",
    ),
    path("registros/", registros, name="painel-registros"),
]
