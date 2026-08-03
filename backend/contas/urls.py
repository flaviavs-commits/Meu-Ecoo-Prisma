from django.urls import path

from .views import DesativarUsuarioView


urlpatterns = [
    path("usuarios/<int:pk>/desativar/", DesativarUsuarioView.as_view(), name="desativar-usuario"),
]
