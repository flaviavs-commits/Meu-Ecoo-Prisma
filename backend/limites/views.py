from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .excecoes import MotivoObrigatorioError
from .permissoes import EProvider
from .serializers import (
    AtualizarPlanoSerializer,
    ConsumoIASerializer,
    EstadoCotaSerializer,
    PlanoSerializer,
)
from .normalizacao import cota_da_conta, percentual_da_conta
from .servico import atualizar_plano, estado_cota, planos_disponiveis
from .models import ConsumoIA


class CotaPropriaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        estado = cota_da_conta(estado_cota(request.user))
        return Response(EstadoCotaSerializer(estado).data)


class HistoricoUsoPagination(PageNumberPagination):
    page_size = 20


class HistoricoUsoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = ConsumoIA.objects.filter(usuario=request.user).order_by("-criado_em")
        paginator = HistoricoUsoPagination()
        pagina = paginator.paginate_queryset(queryset, request)
        # Mesma regua da cota: cada chamada aparece como fatia dos 100% da conta.
        capacidade = estado_cota(request.user).limite_percentual
        return paginator.get_paginated_response(
            ConsumoIASerializer(
                pagina, many=True, context={"capacidade": capacidade}
            ).data
        )


class AtualizarPlanoInstituicaoView(APIView):
    permission_classes = [IsAuthenticated, EProvider]

    def patch(self, request, instituicao_id):
        from contas.models import Instituicao

        try:
            alvo = Instituicao.objects.get(pk=instituicao_id)
        except Instituicao.DoesNotExist:
            return Response(status=404)
        serializer = AtualizarPlanoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            assinatura = atualizar_plano(
                instituicao=alvo,
                ator=request.user,
                codigo=serializer.validated_data["plano"],
                motivo=serializer.validated_data["motivo"],
                periodicidade=serializer.validated_data.get("periodicidade"),
            )
        except MotivoObrigatorioError:
            return Response({"erro": {"codigo": "dados_invalidos"}}, status=400)
        except ValueError as erro:
            return Response({"erro": {"mensagem": str(erro)}}, status=400)
        return Response(
            {
                "instituicao": alvo.id,
                "cota": "plano_atualizado",
                "periodicidade": assinatura.periodicidade,
            }
        )


class PlanosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(PlanoSerializer(planos_disponiveis(), many=True).data)
