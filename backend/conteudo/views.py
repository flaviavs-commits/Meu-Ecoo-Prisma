from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from contas.acoes import AcaoDestrutivaMixin

from .excecoes import (
    ConteudoConflitoError,
    ConteudoConfirmacaoError,
    ConteudoForaDaInstituicaoError,
    ConteudoPermissaoError,
    ConteudoSemQuestoesError,
)
from .models import Material, Prova
from .serializers import MaterialSerializer, ProvaAlunoSerializer, ProvaProfessorSerializer
from .servico import oficializar_prova


class ProvaDetalheView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            prova = Prova.objects.prefetch_related("questoes").get(pk=pk)
        except Prova.DoesNotExist:
            return Response(status=404)
        if prova.instituicao_id != request.user.instituicao_id:
            return Response(status=404)
        if request.user.perfil == "ALUNO":
            if prova.status != "OFICIAL":
                return Response(status=404)
            if not prova.turma.matriculas.filter(aluno=request.user, saiu_em__isnull=True).exists():
                return Response(status=404)
            return Response(ProvaAlunoSerializer(prova).data)
        if request.user.perfil == "PROFESSOR" and prova.status == "RASCUNHO" and prova.autor_id != request.user.id:
            return Response(status=403)
        return Response(ProvaProfessorSerializer(prova).data)


class OficializarProvaView(AcaoDestrutivaMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        erro_confirmacao = self.validar_dados_confirmacao(request)
        if erro_confirmacao:
            return erro_confirmacao
        try:
            prova = Prova.objects.get(pk=pk)
        except Prova.DoesNotExist:
            return Response(status=404)
        if prova.instituicao_id != request.user.instituicao_id:
            return Response(status=404)
        try:
            oficializar_prova(
                prova=prova,
                ator=request.user,
                confirmacao=request.data.get("confirmacao"),
                motivo=request.data.get("motivo"),
            )
        except ConteudoConflitoError:
            return Response(status=409)
        except ConteudoSemQuestoesError:
            return Response(status=422)
        except ConteudoConfirmacaoError:
            return Response(status=400)
        except ConteudoPermissaoError:
            return Response(status=403)
        except ConteudoForaDaInstituicaoError:
            return Response(status=404)
        return Response(ProvaProfessorSerializer(prova).data, status=200)


class MaterialDetalheView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            material = Material.objects.get(pk=pk, instituicao_id=request.user.instituicao_id)
        except Material.DoesNotExist:
            return Response(status=404)
        if (
            request.user.perfil == "ALUNO"
            and material.status != "OFICIAL"
            and material.autor_id != request.user.id
        ):
            return Response(status=404)
        return Response(MaterialSerializer(material).data)
