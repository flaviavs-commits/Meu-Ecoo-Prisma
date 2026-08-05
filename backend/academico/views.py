from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Disciplina, Nota, Turma
from .notas import (
    AcademicoConfirmacaoError,
    AcademicoPermissaoError,
    NotaJaOficialError,
    aprovar_nota,
    consultar_notas,
    lancar_nota,
    registrar_falta,
)
from .serializers import (
    FaltaInputSerializer,
    NotaInputSerializer,
    NotaSerializer,
    TurmaSerializer,
)


class AcademicoPagination(PageNumberPagination):
    page_size = 25


class TurmasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Turma.objects.filter(instituicao_id=request.user.instituicao_id).order_by("id")
        if request.user.perfil == "ALUNO":
            qs = qs.filter(matriculas__aluno=request.user, matriculas__saiu_em__isnull=True)
        elif request.user.perfil == "PROFESSOR":
            qs = qs.filter(professor_responsavel=request.user)
        elif request.user.perfil != "DIRETOR":
            # Sem este ramo, perfil desconhecido (ex.: superadmin, que tem
            # `perfil=None`) caia fora dos dois `if` acima e recebia a listagem
            # institucional inteira em silencio - o oposto do que
            # `consultar_notas` faz para o mesmo usuario, que e negar.
            return Response(status=status.HTTP_403_FORBIDDEN)
        paginator = AcademicoPagination()
        pagina = paginator.paginate_queryset(qs.select_related("disciplina", "professor_responsavel"), request)
        return paginator.get_paginated_response(TurmaSerializer(pagina, many=True).data)


class NotasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            notas = consultar_notas(usuario=request.user).order_by("-criado_em")
        except AcademicoPermissaoError:
            # O POST desta view e o NotaDetalheView ja tratavam esta excecao; so
            # o GET nao, entao perfil sem acesso academico (`perfil=None`, caso
            # do superadmin) devolvia 500 em vez de 403.
            return Response(status=status.HTTP_403_FORBIDDEN)
        paginator = AcademicoPagination()
        pagina = paginator.paginate_queryset(notas, request)
        return paginator.get_paginated_response(NotaSerializer(pagina, many=True).data)

    def post(self, request):
        # Nota fica entre aluno e professor; o diretor so le o que ja foi
        # aprovado (regra de produto, 2026-08-05).
        if request.user.perfil != "PROFESSOR":
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = NotaInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data
        try:
            turma = Turma.objects.get(pk=dados["turma"])
            disciplina = Disciplina.objects.get(pk=dados["disciplina"])
            aluno = get_user_model().objects.get(pk=dados["aluno"])
            nota = lancar_nota(
                turma=turma,
                disciplina=disciplina,
                aluno=aluno,
                valor=dados["valor"],
                avaliacao=dados["avaliacao"],
                ator=request.user,
            )
        except (Turma.DoesNotExist, Disciplina.DoesNotExist, get_user_model().DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)
        except AcademicoPermissaoError as erro:
            return Response(status=404 if erro.codigo == "fora_da_instituicao" else 403)
        return Response(NotaSerializer(nota).data, status=status.HTTP_201_CREATED)


class NotaDetalheView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            nota = Nota.objects.select_related("turma", "disciplina", "aluno").get(pk=pk)
        except Nota.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if nota.turma.instituicao_id != request.user.instituicao_id:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            visivel = consultar_notas(usuario=request.user, aluno_alvo=nota.aluno).filter(pk=pk).exists()
        except AcademicoPermissaoError:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(NotaSerializer(nota).data) if visivel else Response(status=403)


class AprovarNotaView(APIView):
    """Professor revisa e aprova a nota: e o que a torna visivel ao diretor."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            nota = Nota.objects.select_related("turma").get(pk=pk)
        except Nota.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            nota = aprovar_nota(
                nota=nota,
                ator=request.user,
                confirmacao=request.data.get("confirmacao") is True,
                motivo=request.data.get("motivo"),
            )
        except NotaJaOficialError:
            return Response({"erro": {"codigo": "nota_ja_oficial"}}, status=status.HTTP_409_CONFLICT)
        except AcademicoConfirmacaoError as erro:
            return Response({"erro": {"mensagem": str(erro)}}, status=status.HTTP_400_BAD_REQUEST)
        except AcademicoPermissaoError as erro:
            return Response(status=404 if erro.codigo == "fora_da_instituicao" else 403)
        return Response(NotaSerializer(nota).data)


class FaltasView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Mesma regra da nota: lancamento e do professor da turma.
        if request.user.perfil != "PROFESSOR":
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = FaltaInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data
        try:
            turma = Turma.objects.get(pk=dados["turma"])
            aluno = get_user_model().objects.get(pk=dados["aluno"])
            falta = registrar_falta(
                turma=turma,
                aluno=aluno,
                data=dados["data"],
                justificada=dados["justificada"],
                motivo=dados["motivo"],
                ator=request.user,
            )
        except (Turma.DoesNotExist, get_user_model().DoesNotExist):
            return Response(status=404)
        except AcademicoPermissaoError as erro:
            return Response(status=404 if erro.codigo == "fora_da_instituicao" else 403)
        return Response({"id": falta.id}, status=201)
