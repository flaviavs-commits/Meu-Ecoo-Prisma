from django.urls import path

from .views import MaterialDetalheView, OficializarProvaView, ProvaDetalheView

app_name = "conteudo"

urlpatterns = [
    path("provas/<int:pk>/", ProvaDetalheView.as_view(), name="prova-detalhe"),
    path("provas/<int:pk>/oficializar/", OficializarProvaView.as_view(), name="prova-oficializar"),
    path("materiais/<int:pk>/", MaterialDetalheView.as_view(), name="material-detalhe"),
]
