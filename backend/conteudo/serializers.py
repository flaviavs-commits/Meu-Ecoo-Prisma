from rest_framework import serializers

from .models import Material, Prova, Questao


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
        fields = ["id", "titulo", "descricao", "origem", "status", "turma", "disciplina", "arquivo", "criado_em"]
        read_only_fields = fields
