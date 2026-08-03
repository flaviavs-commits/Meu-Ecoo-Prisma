from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import LoginSerializer, EuSerializer
from .throttles import LoginRateThrottle


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh = response.data.pop("refresh", None)
        if refresh:
            response.set_cookie("refresh_token", refresh, httponly=True, secure=True, samesite="Lax", max_age=604800)
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
            response.set_cookie("refresh_token", refresh, httponly=True, secure=True, samesite="Lax", max_age=604800)
        return response


class EuView(APIView):
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
