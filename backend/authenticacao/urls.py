from django.urls import path

from .views import AlterarSenhaView, EsqueciSenhaView, EuView, LoginView, LogoutView, RefreshView

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("refresh/", RefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("eu/", EuView.as_view()),
    path("senha/alterar/", AlterarSenhaView.as_view()),
    path("senha/esquecida/", EsqueciSenhaView.as_view()),
]
