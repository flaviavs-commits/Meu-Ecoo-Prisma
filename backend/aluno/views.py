from django.db.models import Q, Avg, Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from conteudo.models import Material, Simulado, StatusConteudo, StatusSimulado
from limites.normalizacao import cota_da_conta
from limites.servico import estado_cota
from memoria.models import Conversa

from .models import AgendaEstudo, StatusAgenda

from .serializers import DashboardAlunoSerializer


class DashboardAlunoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, "perfil", None) != "ALUNO":
            return Response(status=403)
        materiais = Material.objects.filter(
            Q(instituicao_id=request.user.instituicao_id, status=StatusConteudo.OFICIAL)
            | Q(autor=request.user)
        )
        simulados = Simulado.objects.filter(aluno=request.user)
        conversas = Conversa.objects.filter(aluno=request.user)
        progresso = (
            simulados.filter(status=StatusSimulado.CONCLUIDO)
            .values("disciplina")
            .annotate(media=Avg("resultado_percentual"), total=Count("id"))
            .order_by("disciplina")
        )
        dados = {
            "metricas": {
                "sessoes": conversas.count(),
                "simulados": simulados.count(),
                "materiais": materiais.distinct().count(),
            },
            "cota": cota_da_conta(estado_cota(request.user)),
            "progresso_por_materia": [
                {
                    "disciplina": item["disciplina"],
                    "percentual": item["media"],
                    "simulados": item["total"],
                }
                for item in progresso
            ],
            "recentes": {
                "conversas": list(
                    conversas.values("id", "titulo", "disciplina", "criada_em")[:5]
                ),
                "simulados": list(
                    simulados.values(
                        "id", "disciplina", "status", "resultado_percentual", "criado_em"
                    )[:5]
                ),
                "materiais": list(
                    materiais.distinct().values("id", "titulo", "formato", "criado_em")[:5]
                ),
                "agenda": list(
                    AgendaEstudo.objects.filter(
                        aluno=request.user, status=StatusAgenda.PENDENTE
                    ).values("id", "titulo", "disciplina", "agendado_para")[:5]
                ),
            },
        }
        return Response(DashboardAlunoSerializer(dados).data)
