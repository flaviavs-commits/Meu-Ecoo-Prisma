from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth import login as auth_login

from .serializers import LoginSerializer, EuSerializer
from .throttles import LoginRateThrottle


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as erro:
            raise InvalidToken(erro.args[0]) from erro

        # O painel administrativo usa a sessão nativa do Django. Criá-la
        # somente para superadmin mantém as contas acadêmicas no contrato JWT
        # e permite que o login público encaminhe o administrador ao painel.
        if serializer.user.is_superuser:
            auth_login(request, serializer.user)

        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        refresh = response.data.pop("refresh", None)
        if refresh:
            response.set_cookie(
                "refresh_token", refresh, httponly=True,
                secure=settings.REFRESH_COOKIE_SECURE, samesite="Lax", max_age=604800,
            )
        return response


class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data["refresh"] = request.COOKIES.get("refresh_token", data.get("refresh", ""))
        request._full_data = data
        response = super().post(request, *args, **kwargs)
        refresh = response.data.pop("refresh", None)
        if refresh:
            response.set_cookie(
                "refresh_token", refresh, httponly=True,
                secure=settings.REFRESH_COOKIE_SECURE, samesite="Lax", max_age=604800,
            )
        return response


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh = request.COOKIES.get("refresh_token")
        if refresh:
            try:
                RefreshToken(refresh).blacklist()
            except Exception:  # token ausente ou expirado ja nao pode ser reutilizado
                pass
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie("refresh_token", samesite="Lax")
        return response


class EuView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(EuSerializer(request.user).data)


class AlterarSenhaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        atual = request.data.get("senha_atual", "")
        nova = request.data.get("nova_senha", "")
        if not request.user.check_password(atual):
            return Response({"erro": {"codigo": "senha_invalida", "mensagem": "Senha atual incorreta."}}, status=400)
        if len(nova) < 10:
            return Response({"erro": {"codigo": "senha_fraca", "mensagem": "A nova senha deve ter pelo menos 10 caracteres."}}, status=400)
        request.user.set_password(nova)
        request.user.save(update_fields=["password"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class EsqueciSenhaView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response({"mensagem": "Se o e-mail existir, enviaremos instrucoes de recuperacao."})
