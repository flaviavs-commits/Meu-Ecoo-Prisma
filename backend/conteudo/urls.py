from django.urls import path

from .views import MaterialDetalheView, OficializarProvaView, ProvaDetalheView
from .material_views import GerarMaterialView, MateriaisView
from .simulado_views import (
    FinalizarSimuladoView,
    GerarSimuladoView,
    ResponderSimuladoView,
    SimuladoDetalheView,
    SimuladosView,
)

app_name = "conteudo"

urlpatterns = [
    path("materiais/", MateriaisView.as_view(), name="materiais"),
    path("materiais/gerar/", GerarMaterialView.as_view(), name="material-gerar"),
    path("simulados/", SimuladosView.as_view(), name="simulados"),
    path("simulados/gerar/", GerarSimuladoView.as_view(), name="simulado-gerar"),
    path("simulados/<int:pk>/", SimuladoDetalheView.as_view(), name="simulado-detalhe"),
    path(
        "simulados/<int:pk>/questoes/<int:questao_id>/responder/",
        ResponderSimuladoView.as_view(),
        name="simulado-responder",
    ),
    path("simulados/<int:pk>/finalizar/", FinalizarSimuladoView.as_view(), name="simulado-finalizar"),
    path("provas/<int:pk>/", ProvaDetalheView.as_view(), name="prova-detalhe"),
    path("provas/<int:pk>/oficializar/", OficializarProvaView.as_view(), name="prova-oficializar"),
    path("materiais/<int:pk>/", MaterialDetalheView.as_view(), name="material-detalhe"),
]
