from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView

from .views import AlterarSenhaView, EsqueciSenhaView, EuView, LoginView, RefreshView

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("refresh/", RefreshView.as_view()),
    path("logout/", TokenBlacklistView.as_view()),
    path("eu/", EuView.as_view()),
    path("senha/alterar/", AlterarSenhaView.as_view()),
    path("senha/esquecida/", EsqueciSenhaView.as_view()),
]
