from django.urls import path

from .views import dashboard, usuario, usuario_perfil, usuarios


urlpatterns = [
    path("", dashboard, name="painel-dashboard"),
    path("usuarios/", usuarios, name="painel-usuarios"),
    path("usuarios/<int:pk>/", usuario, name="painel-usuario"),
    path("usuarios/<int:pk>/perfil/", usuario_perfil, name="painel-usuario-perfil"),
]
