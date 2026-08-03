from rest_framework.response import Response
from rest_framework import status

from .auditoria import RegistroDeAuditoria


class AcaoDestrutivaMixin:
    acao_auditoria = "acao_destrutiva"

    def validar_dados_confirmacao(self, request):
        if request.data.get("confirmacao") is not True:
            return Response({"erro": {"codigo": "confirmacao_obrigatoria", "mensagem": "Confirme a acao para continuar."}}, status=status.HTTP_400_BAD_REQUEST)
        motivo = str(request.data.get("motivo", "")).strip()
        if not motivo:
            return Response({"erro": {"codigo": "motivo_obrigatorio", "mensagem": "Informe o motivo da acao."}}, status=status.HTTP_400_BAD_REQUEST)
        return None

    def validar_confirmacao(self, request, objeto):
        erro = self.validar_dados_confirmacao(request)
        if erro:
            return erro
        motivo = str(request.data.get("motivo", "")).strip()
        RegistroDeAuditoria.objects.create(ator=self.request.user, acao=self.acao_auditoria, objeto_tipo=objeto.__class__.__name__, objeto_id=objeto.pk, motivo=motivo)
        return None
