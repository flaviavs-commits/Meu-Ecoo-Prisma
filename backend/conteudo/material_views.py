from django.db.models import Q
from academico.models import Disciplina
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ia.gateway import GatewayIA
from limites.excecoes import LimiteDeUsoExcedidoError

from .models import FormatoMaterial, Material, OrigemConteudo
from .serializers import GerarMaterialSerializer, MaterialSerializer
from .servico import criar_material


class MaterialPagination(PageNumberPagination):
    page_size = 24


class MateriaisView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Material.objects.filter(
            instituicao_id=request.user.instituicao_id
        ).filter(Q(status="OFICIAL") | Q(autor=request.user))
        busca = request.query_params.get("q", "").strip()
        formato = request.query_params.get("formato", "").strip().upper()
        if busca:
            queryset = queryset.filter(
                Q(titulo__icontains=busca) | Q(descricao__icontains=busca)
            )
        if formato in FormatoMaterial.values:
            queryset = queryset.filter(formato=formato)
        paginator = MaterialPagination()
        pagina = paginator.paginate_queryset(
            queryset.order_by("-criado_em", "-id"), request
        )
        return paginator.get_paginated_response(MaterialSerializer(pagina, many=True).data)


class GerarMaterialView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if getattr(request.user, "perfil", None) not in {"ALUNO", "PROFESSOR"}:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = GerarMaterialSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data
        try:
            chamada, texto = GatewayIA.from_settings().chamar(
                instituicao=request.user.instituicao,
                usuario=request.user,
                classe_tarefa="RESUMO",
                prompt=dados["conteudo"],
                devolver_texto=True,
            )
        except LimiteDeUsoExcedidoError as erro:
            return Response({"erro": {"codigo": erro.codigo}}, status=422)
        disciplina = Disciplina.objects.filter(
            instituicao_id=request.user.instituicao_id,
            nome__iexact=dados.get("disciplina", "").strip(),
        ).first()
        material = criar_material(
            instituicao=request.user.instituicao,
            turma=None,
            disciplina=disciplina,
            autor=request.user,
            titulo=dados["titulo"],
            origem=OrigemConteudo.IA,
            formato=dados["formato"],
            descricao=texto,
            chamada_ia=chamada,
        )
        return Response(MaterialSerializer(material).data, status=status.HTTP_201_CREATED)
