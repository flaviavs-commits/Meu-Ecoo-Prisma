from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from limites.excecoes import LimiteDeUsoExcedidoError

from .models import Conversa
from .serializers import (
    ConfiguracaoTutorSerializer,
    ConversaListaSerializer,
    ConversaSerializer,
    CriarConversaSerializer,
    CriarMensagemSerializer,
    MensagemSerializer,
)
from .tutor import criar_conversa, obter_configuracao, responder_mensagem


class ConversaPagination(PageNumberPagination):
    page_size = 20


class ConversasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, "perfil", None) != "ALUNO":
            return Response(status=status.HTTP_403_FORBIDDEN)
        queryset = Conversa.objects.filter(aluno=request.user).order_by("-criada_em", "-id")
        paginator = ConversaPagination()
        pagina = paginator.paginate_queryset(queryset, request)
        return paginator.get_paginated_response(ConversaListaSerializer(pagina, many=True).data)

    def post(self, request):
        if getattr(request.user, "perfil", None) != "ALUNO":
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = CriarConversaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversa = criar_conversa(aluno=request.user, **serializer.validated_data)
        return Response(ConversaSerializer(conversa).data, status=status.HTTP_201_CREATED)


class ConversaDetalheView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        if getattr(request.user, "perfil", None) != "ALUNO":
            return Response(status=403)
        try:
            conversa = Conversa.objects.get(pk=pk, aluno_id=request.user.id)
        except Conversa.DoesNotExist:
            return Response(status=404)
        return Response(ConversaSerializer(conversa).data)


class MensagensConversaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if getattr(request.user, "perfil", None) != "ALUNO":
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            conversa = Conversa.objects.get(pk=pk, aluno=request.user)
        except Conversa.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CriarMensagemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            mensagem_aluno, mensagem_tutor = responder_mensagem(
                conversa=conversa,
                conteudo=serializer.validated_data["conteudo"],
            )
        except LimiteDeUsoExcedidoError as erro:
            return Response(
                {"erro": {"codigo": erro.codigo}}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        except ValueError as erro:
            return Response({"erro": {"mensagem": str(erro)}}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "mensagem_aluno": MensagemSerializer(mensagem_aluno).data,
                "mensagem_tutor": MensagemSerializer(mensagem_tutor).data,
            },
            status=status.HTTP_201_CREATED,
        )


class ConfiguracaoTutorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, "perfil", None) != "ALUNO":
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(ConfiguracaoTutorSerializer(obter_configuracao(request.user)).data)

    def patch(self, request):
        if getattr(request.user, "perfil", None) != "ALUNO":
            return Response(status=status.HTTP_403_FORBIDDEN)
        configuracao = obter_configuracao(request.user)
        serializer = ConfiguracaoTutorSerializer(configuracao, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
