from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversa
from .serializers import ConversaSerializer


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
