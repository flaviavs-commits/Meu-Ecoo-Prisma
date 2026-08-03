from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from contas.permissoes.e_diretor import EDiretor

from . import alocacao as alocacao_service
from .alerta import estado_alerta_usuario
from .excecoes import AlocacaoForaDaInstituicaoError, AlocacaoSemConfirmacaoError
from .models import Lancamento
from .saldo import saldo_instituicao, saldo_usuario
from .serializers import (
    AlocacaoSerializer,
    AlertaSaldoSerializer,
    LancamentoSerializer,
    ReducaoAlocacaoSerializer,
    SaldoSerializer,
)

# NOTA (risco assumido, ver diario de E05): permissao por perfil aqui e provisoria,
# checada por `request.user.perfil` direto. Quando E04 (autorizacao e perfis)
# existir, isto deve trocar para a permission class real dela.


class SaldoProprioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        dados = SaldoSerializer({"saldo": saldo_usuario(request.user.id)}).data
        return Response(dados)


class AlertaSaldoProprioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        dados = AlertaSaldoSerializer(estado_alerta_usuario(request.user)).data
        return Response(dados)


class SaldoInstituicaoView(APIView):
    permission_classes = [IsAuthenticated, EDiretor]

    def get(self, request):
        dados = SaldoSerializer({"saldo": saldo_instituicao(request.user.instituicao_id)}).data
        return Response(dados)


class LancamentoPagination(PageNumberPagination):
    page_size = 20


class LancamentosView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = LancamentoPagination

    def get(self, request):
        qs = Lancamento.objects.filter(instituicao_id=request.user.instituicao_id)
        if getattr(request.user, "perfil", None) != "DIRETOR":
            qs = qs.filter(usuario_id=request.user.id)
        qs = qs.order_by("-criado_em")
        paginator = self.pagination_class()
        pagina = paginator.paginate_queryset(qs, request)
        dados = LancamentoSerializer(pagina, many=True).data
        return paginator.get_paginated_response(dados)


class AlocacoesView(APIView):
    permission_classes = [IsAuthenticated, EDiretor]

    def post(self, request):
        serializer = AlocacaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data
        usuario_destino = None
        try:
            if dados.get("destino_usuario"):
                usuario_destino = get_user_model().objects.get(pk=dados["destino_usuario"])
            alocacao_service.alocar(
                instituicao=request.user.instituicao,
                destino_usuario=usuario_destino,
                destino_turma_id=dados.get("destino_turma"),
                quantidade=dados["quantidade"],
                motivo=dados["motivo"],
                criado_por=request.user,
            )
        except get_user_model().DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except AlocacaoForaDaInstituicaoError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_201_CREATED)


class ReduzirAlocacaoView(APIView):
    permission_classes = [IsAuthenticated, EDiretor]

    def post(self, request):
        serializer = ReducaoAlocacaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data
        usuario_origem = None
        if dados.get("origem_usuario"):
            usuario_origem = get_user_model().objects.get(pk=dados["origem_usuario"])
        try:
            alocacao_service.reduzir_alocacao(
                instituicao=request.user.instituicao,
                origem_usuario=usuario_origem,
                origem_turma_id=dados.get("origem_turma"),
                quantidade=dados["quantidade"],
                motivo=dados["motivo"],
                criado_por=request.user,
                confirmado=dados["confirmacao"],
            )
        except AlocacaoSemConfirmacaoError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)
