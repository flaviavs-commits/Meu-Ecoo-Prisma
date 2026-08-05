from rest_framework import serializers

from .models import ConsumoIA


class EstadoCotaSerializer(serializers.Serializer):
    ciclo = serializers.CharField()
    limite_percentual = serializers.DecimalField(max_digits=8, decimal_places=4)
    consumido_percentual = serializers.DecimalField(max_digits=14, decimal_places=4)
    disponivel_percentual = serializers.DecimalField(max_digits=14, decimal_places=4)
    bloqueado = serializers.BooleanField()


class ConsumoIASerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumoIA
        fields = [
            "id",
            "fornecedor",
            "modelo",
            "classe_tarefa",
            "ciclo",
            "percentual",
            "criado_em",
        ]
        read_only_fields = fields


class AtualizarPlanoSerializer(serializers.Serializer):
    plano = serializers.CharField(max_length=16)
    motivo = serializers.CharField(min_length=3, trim_whitespace=True)


class PlanoSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    nome = serializers.CharField()
    preco_por_conta = serializers.DecimalField(max_digits=10, decimal_places=2)
    limite_percentual_por_conta = serializers.DecimalField(max_digits=8, decimal_places=4)
