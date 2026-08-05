from rest_framework import serializers

from limites.serializers import EstadoCotaSerializer


class DashboardAlunoSerializer(serializers.Serializer):
    metricas = serializers.DictField()
    cota = EstadoCotaSerializer()
    progresso_por_materia = serializers.ListField()
    recentes = serializers.DictField()
