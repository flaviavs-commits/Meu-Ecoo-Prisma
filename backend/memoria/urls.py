from django.urls import path

from .views import ConversaDetalheView

app_name = "memoria"

urlpatterns = [
    path("conversas/<int:pk>/", ConversaDetalheView.as_view(), name="conversa-detalhe"),
]
