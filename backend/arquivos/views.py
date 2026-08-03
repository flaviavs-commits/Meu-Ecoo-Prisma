from django.http import FileResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .excecoes import ArquivoError
from .models import Arquivo
from .normalizacao import nome_seguro
from .serializers import ArquivoUploadSerializer
from .servico import enviar_arquivo
from .storage import StorageAdapter


class ArquivoUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if getattr(request.user, "perfil", None) not in {"ALUNO", "PROFESSOR"}:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = ArquivoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            registro = enviar_arquivo(
                instituicao=request.user.instituicao,
                enviado_por=request.user,
                arquivo=serializer.validated_data["arquivo"],
            )
        except ArquivoError as erro:
            return Response(
                {"erro": {"codigo": erro.codigo, "mensagem": "Arquivo recusado."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"id": registro.id, "nome_original": registro.nome_original}, status=201)


class ArquivoDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            registro = Arquivo.objects.get(
                pk=pk, instituicao_id=request.user.instituicao_id
            )
        except Arquivo.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        resposta = FileResponse(
            StorageAdapter().open(registro.arquivo.name), content_type=registro.tipo_mime
        )
        resposta["Content-Disposition"] = (
            f'attachment; filename="{nome_seguro(registro.nome_original)}"'
        )
        resposta["X-Content-Type-Options"] = "nosniff"
        return resposta
