from django.urls import include, path

urlpatterns = [
    path("api/v1/", include("core.urls")),
    path("api/v1/auth/", include("authenticacao.urls")),
    path("api/v1/creditos/", include("creditos.urls")),
    path("api/v1/memoria/", include("memoria.urls")),
    path("api/v1/arquivos/", include("arquivos.urls")),
    path("api/v1/academico/", include("academico.urls")),
    path("api/v1/conteudo/", include("conteudo.urls")),
]

handler404 = "core.erros.pagina_nao_encontrada"
