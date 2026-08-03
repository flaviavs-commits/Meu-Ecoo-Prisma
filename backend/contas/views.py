from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .desativacao import DesativacaoNegada, desativar_usuario
from .models import Usuario


class DesativarUsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        queryset = Usuario.objects.filter(pk=pk)
        if not request.user.is_staff:
            queryset = queryset.filter(instituicao_id=request.user.instituicao_id)
        alvo = get_object_or_404(queryset)
        try:
            desativar_usuario(
                alvo=alvo,
                ator=request.user,
                confirmacao=request.data.get("confirmacao") is True,
                motivo=request.data.get("motivo"),
            )
        except DesativacaoNegada as erro:
            return Response({"erro": str(erro)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)
