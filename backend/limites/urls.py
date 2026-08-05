from django.urls import path

from .views import (
    AtualizarPlanoInstituicaoView,
    CotaPropriaView,
    HistoricoUsoView,
    PlanosView,
)

app_name = "limites"

urlpatterns = [
    path("uso/", CotaPropriaView.as_view(), name="uso-proprio"),
    path("uso/historico/", HistoricoUsoView.as_view(), name="uso-historico"),
    path("planos/", PlanosView.as_view(), name="planos"),
    path(
        "instituicoes/<int:instituicao_id>/plano/",
        AtualizarPlanoInstituicaoView.as_view(),
        name="plano-instituicao",
    ),
]
