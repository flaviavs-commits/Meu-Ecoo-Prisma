from django.urls import path

from .views import AprovarNotaView, FaltasView, NotaDetalheView, NotasView, TurmasView

app_name = "academico"

urlpatterns = [
    path("turmas/", TurmasView.as_view(), name="turmas"),
    path("notas/", NotasView.as_view(), name="notas"),
    path("notas/<int:pk>/", NotaDetalheView.as_view(), name="nota-detalhe"),
    path("notas/<int:pk>/aprovar/", AprovarNotaView.as_view(), name="nota-aprovar"),
    path("faltas/", FaltasView.as_view(), name="faltas"),
]
