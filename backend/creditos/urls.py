from django.urls import path

from . import views

app_name = "creditos"

urlpatterns = [
    path("saldo/", views.SaldoProprioView.as_view(), name="saldo-proprio"),
    path("saldo/alerta/", views.AlertaSaldoProprioView.as_view(), name="saldo-alerta"),
    path("saldo/instituicao/", views.SaldoInstituicaoView.as_view(), name="saldo-instituicao"),
    path("lancamentos/", views.LancamentosView.as_view(), name="lancamentos"),
    path("alocacoes/", views.AlocacoesView.as_view(), name="alocacoes"),
    path("alocacoes/reduzir/", views.ReduzirAlocacaoView.as_view(), name="alocacoes-reduzir"),
]

# NOTA: este urls.py ainda nao esta incluido em `config/urls.py` (arquivo do
# agente de E01) para nao competir com quem esta escrevendo o roteador raiz
# agora. Quem fechar E01/E04 inclui:
#   path("api/v1/creditos/", include("creditos.urls"))
