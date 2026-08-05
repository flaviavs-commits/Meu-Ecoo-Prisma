from django.urls import path

from .views import DashboardAlunoView
from .views_agenda import AgendaEstudoDetalheView, AgendaEstudoView

app_name = "aluno"

urlpatterns = [
    path("dashboard/", DashboardAlunoView.as_view(), name="dashboard"),
    path("agenda/", AgendaEstudoView.as_view(), name="agenda"),
    path("agenda/<int:pk>/", AgendaEstudoDetalheView.as_view(), name="agenda-detalhe"),
]
