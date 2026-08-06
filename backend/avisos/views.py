from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from academico.models import Turma

from .excecoes import AvisoPermissaoError
from .serializers import AvisoSerializer, EnviarAvisoSerializer
from .servico import avisos_visiveis, enviar_aviso


class AvisoPagination(PageNumberPagination):
    page_size = 20


class AvisosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        paginator = AvisoPagination()
        pagina = paginator.paginate_queryset(
            avisos_visiveis(request.user).select_related("turma", "autor"), request
        )
        return paginator.get_paginated_response(AvisoSerializer(pagina, many=True).data)

    def post(self, request):
        serializer = EnviarAvisoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data
        # Filtra pela instituicao antes de existir: sem isso, o 404 e o 403
        # distinguiriam turma de outra escola de turma inexistente.
        turma = Turma.objects.filter(
            pk=dados["turma"], instituicao_id=request.user.instituicao_id
        ).first()
        if turma is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            aviso = enviar_aviso(
                turma=turma,
                autor=request.user,
                titulo=dados["titulo"],
                mensagem=dados["mensagem"],
                prazo_entrega=dados.get("prazo_entrega"),
            )
        except AvisoPermissaoError as erro:
            return Response(
                {"erro": {"codigo": erro.codigo, "mensagem": str(erro)}},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValueError as erro:
            return Response(
                {"erro": {"codigo": "dados_invalidos", "mensagem": str(erro)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(AvisoSerializer(aviso).data, status=status.HTTP_201_CREATED)
