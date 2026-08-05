from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ia.excecoes import ChamadaConcorrenteError, ProvedorIAError
from limites.excecoes import LimiteDeUsoExcedidoError

from .excecoes import SimuladoIndisponivelError
from .models import Simulado
from .serializers import (
    GerarSimuladoSerializer,
    SimuladoResultadoSerializer,
    SimuladoSerializer,
)
from .simulados import finalizar_simulado, gerar_simulado, responder_questao


class SimuladoPagination(PageNumberPagination):
    page_size = 20


class SimuladosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, "perfil", None) != "ALUNO":
            return Response(status=status.HTTP_403_FORBIDDEN)
        queryset = Simulado.objects.filter(aluno=request.user).prefetch_related("questoes")
        paginator = SimuladoPagination()
        pagina = paginator.paginate_queryset(queryset, request)
        return paginator.get_paginated_response(SimuladoSerializer(pagina, many=True).data)


class GerarSimuladoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if getattr(request.user, "perfil", None) != "ALUNO":
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = GerarSimuladoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            simulado = gerar_simulado(aluno=request.user, **serializer.validated_data)
        except LimiteDeUsoExcedidoError as erro:
            return Response({"erro": {"codigo": erro.codigo}}, status=422)
        except ChamadaConcorrenteError as erro:
            return Response(
                {"erro": {"codigo": erro.codigo, "mensagem": str(erro)}},
                status=status.HTTP_409_CONFLICT,
            )
        except (SimuladoIndisponivelError, ProvedorIAError) as erro:
            # Sem questoes utilizaveis o simulado nao e criado. Antes disso
            # cair aqui, o servico fabricava questao generica com gabarito
            # fixo e devolvia 201 como se tivesse dado certo.
            return Response(
                {"erro": {"codigo": erro.codigo, "mensagem": str(erro)}},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(SimuladoSerializer(simulado).data, status=status.HTTP_201_CREATED)


class SimuladoDetalheView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        if getattr(request.user, "perfil", None) != "ALUNO":
            return Response(status=status.HTTP_403_FORBIDDEN)
        simulado = get_object_or_404(Simulado.objects.prefetch_related("questoes"), pk=pk)
        if simulado.aluno_id != request.user.id:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = (
            SimuladoResultadoSerializer(simulado)
            if simulado.status == "CONCLUIDO"
            else SimuladoSerializer(simulado)
        )
        return Response(serializer.data)


class ResponderSimuladoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, questao_id):
        if getattr(request.user, "perfil", None) != "ALUNO":
            return Response(status=status.HTTP_403_FORBIDDEN)
        simulado = get_object_or_404(Simulado, pk=pk, aluno=request.user)
        questao = get_object_or_404(simulado.questoes, pk=questao_id)
        try:
            responder_questao(
                simulado=simulado,
                questao=questao,
                alternativa=request.data.get("alternativa"),
            )
        except ValueError as erro:
            return Response({"erro": {"mensagem": str(erro)}}, status=400)
        return Response({"id": questao.id, "resposta": questao.resposta})


class FinalizarSimuladoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if getattr(request.user, "perfil", None) != "ALUNO":
            return Response(status=status.HTTP_403_FORBIDDEN)
        simulado = get_object_or_404(
            Simulado.objects.prefetch_related("questoes"), pk=pk, aluno=request.user
        )
        finalizar_simulado(simulado=simulado)
        return Response(SimuladoResultadoSerializer(simulado).data)
