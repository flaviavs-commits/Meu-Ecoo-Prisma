from rest_framework import serializers

from .models import ConsumoIA, Periodicidade
from .normalizacao import percentual_da_conta


class EstadoCotaSerializer(serializers.Serializer):
    ciclo = serializers.CharField()
    limite_percentual = serializers.DecimalField(max_digits=8, decimal_places=4)
    consumido_percentual = serializers.DecimalField(max_digits=14, decimal_places=4)
    disponivel_percentual = serializers.DecimalField(max_digits=14, decimal_places=4)
    bloqueado = serializers.BooleanField()


class ConsumoIASerializer(serializers.ModelSerializer):
    """Histórico de uso como a conta o enxerga: percentual e mais nada.

    O modelo guarda `fornecedor`, `modelo` e `custo_bruto`, mas isso é
    telemetria técnica server-side. A conta vê quanto do plano gastou, não
    quanto custou nem qual provedor atendeu — a plataforma opera vários
    provedores e a conversão custo→percentual é ajustada conforme a demanda
    geral do aplicativo, então expor o provedor exporia uma mecânica que muda
    debaixo do usuário e não significa nada para ele.
    """

    percentual = serializers.SerializerMethodField()

    class Meta:
        model = ConsumoIA
        fields = [
            "id",
            "classe_tarefa",
            "ciclo",
            "percentual",
            "criado_em",
        ]
        read_only_fields = fields

    def get_percentual(self, consumo):
        # Formatado como string, igual aos `DecimalField` do resto do contrato
        # (`COERCE_DECIMAL_TO_STRING`): quem consome não deve ver dois tipos
        # diferentes para o mesmo conceito.
        return f"{percentual_da_conta(consumo.percentual, self.context['capacidade']):.4f}"


class AtualizarPlanoSerializer(serializers.Serializer):
    plano = serializers.CharField(max_length=16)
    motivo = serializers.CharField(min_length=3, trim_whitespace=True)
    # Opcional: sem o campo, a assinatura mantem a periodicidade vigente.
    periodicidade = serializers.ChoiceField(
        choices=Periodicidade.choices, required=False, allow_null=True
    )


class PlanoSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    nome = serializers.CharField()
    preco_por_conta = serializers.DecimalField(max_digits=10, decimal_places=2)
    limite_percentual_por_conta = serializers.DecimalField(max_digits=8, decimal_places=4)
