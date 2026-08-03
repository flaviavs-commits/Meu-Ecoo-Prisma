from django.urls import include, path

urlpatterns = [
    path("api/v1/", include("core.urls")),
]

handler404 = "core.erros.pagina_nao_encontrada"
