from django.urls import path

from .views import (
    ConfiguracaoTutorView,
    ConversaDetalheView,
    ConversasView,
    MensagensConversaView,
)

app_name = "memoria"

urlpatterns = [
    path("tutor/configuracao/", ConfiguracaoTutorView.as_view(), name="tutor-configuracao"),
    path("conversas/", ConversasView.as_view(), name="conversas"),
    path("conversas/<int:pk>/", ConversaDetalheView.as_view(), name="conversa-detalhe"),
    path(
        "conversas/<int:pk>/mensagens/",
        MensagensConversaView.as_view(),
        name="conversa-mensagens",
    ),
]
