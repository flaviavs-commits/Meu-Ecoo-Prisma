from rest_framework import serializers

from .models import AgendaEstudo, StatusAgenda


class AgendaEstudoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgendaEstudo
        fields = [
            "id",
            "titulo",
            "disciplina",
            "descricao",
            "agendado_para",
            "status",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = ["id", "criado_em", "atualizado_em"]

    def validate_status(self, value):
        if value not in StatusAgenda.values:
            raise serializers.ValidationError("Status de agenda invalido.")
        return value
