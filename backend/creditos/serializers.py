from decimal import Decimal

from rest_framework import serializers

from .models import Lancamento


class LancamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lancamento
        fields = [
            "id", "instituicao", "usuario", "turma", "tipo",
            "quantidade", "motivo", "referencia", "criado_por", "criado_em",
        ]
        read_only_fields = fields


class SaldoSerializer(serializers.Serializer):
    saldo = serializers.DecimalField(max_digits=14, decimal_places=4)


class AlertaSaldoSerializer(serializers.Serializer):
    saldo = serializers.DecimalField(max_digits=14, decimal_places=4)
    limiar = serializers.DecimalField(
        max_digits=14, decimal_places=4, allow_null=True
    )
    saldo_baixo = serializers.BooleanField()


class AlocacaoSerializer(serializers.Serializer):
    destino_usuario = serializers.IntegerField(required=False, allow_null=True)
    destino_turma = serializers.IntegerField(required=False, allow_null=True)
    quantidade = serializers.DecimalField(
        max_digits=14, decimal_places=4, min_value=Decimal("0.0001")
    )
    motivo = serializers.CharField()


class ReducaoAlocacaoSerializer(serializers.Serializer):
    origem_usuario = serializers.IntegerField(required=False, allow_null=True)
    origem_turma = serializers.IntegerField(required=False, allow_null=True)
    quantidade = serializers.DecimalField(
        max_digits=14, decimal_places=4, min_value=Decimal("0.0001")
    )
    motivo = serializers.CharField()
    confirmacao = serializers.BooleanField(required=False, default=False)
