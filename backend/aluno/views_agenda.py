from datetime import datetime

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AgendaEstudo
from .serializers_agenda import AgendaEstudoSerializer


class AgendaEstudoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.perfil != "ALUNO":
            return Response(status=status.HTTP_403_FORBIDDEN)
        queryset = AgendaEstudo.objects.filter(aluno=request.user)
        inicio = request.query_params.get("de")
        fim = request.query_params.get("ate")
        try:
            if inicio:
                queryset = queryset.filter(agendado_para__gte=_data(inicio))
            if fim:
                queryset = queryset.filter(agendado_para__lte=_data(fim))
        except ValueError as erro:
            return Response({"erro": {"mensagem": str(erro)}}, status=status.HTTP_400_BAD_REQUEST)
        return Response(AgendaEstudoSerializer(queryset, many=True).data)

    def post(self, request):
        if request.user.perfil != "ALUNO":
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = AgendaEstudoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        agenda = serializer.save(aluno=request.user, instituicao=request.user.instituicao)
        return Response(AgendaEstudoSerializer(agenda).data, status=status.HTTP_201_CREATED)


class AgendaEstudoDetalheView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        if request.user.perfil != "ALUNO":
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            agenda = AgendaEstudo.objects.get(pk=pk, aluno=request.user)
        except AgendaEstudo.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AgendaEstudoSerializer(agenda, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


def _data(valor):
    try:
        return datetime.fromisoformat(valor)
    except ValueError as erro:
        raise ValueError("Data de agenda invalida.") from erro
