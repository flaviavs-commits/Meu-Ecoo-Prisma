from rest_framework import serializers

from .models import QuestaoSimulado, Simulado, Material, Prova, Questao


class QuestaoProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questao
        fields = ["id", "ordem", "enunciado", "alternativas", "gabarito"]


class QuestaoAlunoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questao
        fields = ["id", "ordem", "enunciado", "alternativas"]


class ProvaProfessorSerializer(serializers.ModelSerializer):
    questoes = QuestaoProfessorSerializer(many=True, read_only=True)

    class Meta:
        model = Prova
        fields = ["id", "titulo", "origem", "status", "turma", "disciplina", "questoes", "revisado_por", "revisado_em"]


class ProvaAlunoSerializer(serializers.ModelSerializer):
    questoes = QuestaoAlunoSerializer(many=True, read_only=True)

    class Meta:
        model = Prova
        fields = ["id", "titulo", "origem", "status", "turma", "disciplina", "questoes"]


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ["id", "titulo", "descricao", "formato", "origem", "status", "turma", "disciplina", "arquivo", "criado_em"]
        read_only_fields = fields


class GerarMaterialSerializer(serializers.Serializer):
    titulo = serializers.CharField(max_length=200)
    disciplina = serializers.CharField(max_length=120, required=False, allow_blank=True)
    formato = serializers.ChoiceField(
        choices=["MATERIAL", "RESUMO", "FLASHCARDS", "AUDIO"], default="RESUMO"
    )
    conteudo = serializers.CharField(max_length=20000)


class GerarSimuladoSerializer(serializers.Serializer):
    disciplina = serializers.CharField(max_length=120)
    estilo = serializers.CharField(max_length=40, required=False, default="ENEM")
    quantidade = serializers.IntegerField(min_value=1, max_value=50, default=15)
    foco_dificuldades = serializers.BooleanField(required=False, default=True)
    correcao_comentada = serializers.BooleanField(required=False, default=True)


class QuestaoSimuladoSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestaoSimulado
        fields = ["id", "ordem", "enunciado", "alternativas", "resposta"]
        read_only_fields = fields


class SimuladoSerializer(serializers.ModelSerializer):
    questoes = QuestaoSimuladoSerializer(many=True, read_only=True)

    class Meta:
        model = Simulado
        fields = [
            "id",
            "disciplina",
            "estilo",
            "quantidade",
            "foco_dificuldades",
            "correcao_comentada",
            "status",
            "resultado_percentual",
            "criado_em",
            "concluido_em",
            "questoes",
        ]
        read_only_fields = fields


class QuestaoSimuladoResultadoSerializer(serializers.ModelSerializer):
    correta = serializers.SerializerMethodField()

    class Meta:
        model = QuestaoSimulado
        fields = [
            "id",
            "ordem",
            "enunciado",
            "alternativas",
            "resposta",
            "gabarito",
            "correta",
        ]
        read_only_fields = fields

    def get_correta(self, obj):
        return obj.resposta == obj.gabarito


class SimuladoResultadoSerializer(SimuladoSerializer):
    questoes = QuestaoSimuladoResultadoSerializer(many=True, read_only=True)
