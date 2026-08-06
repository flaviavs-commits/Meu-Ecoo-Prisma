from rest_framework import serializers

from .models import Aviso


class AvisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aviso
        fields = [
            "id",
            "turma",
            "autor",
            "titulo",
            "mensagem",
            "prazo_entrega",
            "criado_em",
        ]
        read_only_fields = fields


class EnviarAvisoSerializer(serializers.Serializer):
    turma = serializers.IntegerField()
    titulo = serializers.CharField(max_length=200, trim_whitespace=True)
    mensagem = serializers.CharField(trim_whitespace=True)
    prazo_entrega = serializers.DateTimeField(required=False, allow_null=True)
