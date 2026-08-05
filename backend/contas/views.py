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
        # So o superadmin enxerga fora do proprio tenant. Antes esta guarda era
        # `is_staff`, o que deixava qualquer conta com a flag alcancar usuario
        # de outra instituicao (o 404 abaixo e o que protege o tenant).
        if not request.user.eh_mantenedor:
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
            codigo_status = (
                status.HTTP_403_FORBIDDEN
                if erro.codigo == "sem_permissao"
                else status.HTTP_400_BAD_REQUEST
            )
            return Response({"erro": str(erro)}, status=codigo_status)
        return Response(status=status.HTTP_204_NO_CONTENT)
