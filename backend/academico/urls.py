from django.urls import path

from .views import FaltasView, NotaDetalheView, NotasView, TurmasView

app_name = "academico"

urlpatterns = [
    path("turmas/", TurmasView.as_view(), name="turmas"),
    path("notas/", NotasView.as_view(), name="notas"),
    path("notas/<int:pk>/", NotaDetalheView.as_view(), name="nota-detalhe"),
    path("faltas/", FaltasView.as_view(), name="faltas"),
]
