from rest_framework import serializers

from .models import Falta, Nota, Turma


class TurmaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turma
        fields = [
            "id", "nome", "instituicao", "disciplina",
            "professor_responsavel", "professores",
        ]
        read_only_fields = fields


class NotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nota
        fields = ["id", "turma", "disciplina", "aluno", "avaliacao", "valor", "origem", "oficial", "criado_em", "alterado_em"]
        read_only_fields = ["id", "origem", "oficial", "criado_em", "alterado_em"]


class NotaInputSerializer(serializers.Serializer):
    turma = serializers.IntegerField()
    disciplina = serializers.IntegerField()
    aluno = serializers.IntegerField()
    avaliacao = serializers.CharField(max_length=120)
    valor = serializers.DecimalField(max_digits=6, decimal_places=2)


class FaltaInputSerializer(serializers.Serializer):
    turma = serializers.IntegerField()
    aluno = serializers.IntegerField()
    data = serializers.DateField()
    justificada = serializers.BooleanField(required=False, default=False)
    motivo = serializers.CharField(required=False, allow_blank=True, default="")
