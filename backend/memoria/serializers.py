from rest_framework import serializers

from .models import ConfiguracaoTutor, Conversa, Mensagem


class MensagemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensagem
        fields = ["id", "papel", "conteudo", "criada_em"]
        read_only_fields = fields


class ConversaSerializer(serializers.ModelSerializer):
    mensagens = MensagemSerializer(many=True, read_only=True)

    class Meta:
        model = Conversa
        fields = ["id", "titulo", "disciplina", "topico", "criada_em", "mensagens"]
        read_only_fields = fields


class ConversaListaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversa
        fields = ["id", "titulo", "disciplina", "topico", "criada_em"]
        read_only_fields = fields


class CriarConversaSerializer(serializers.Serializer):
    titulo = serializers.CharField(max_length=200, required=False, allow_blank=True)
    disciplina = serializers.CharField(max_length=120, required=False, allow_blank=True)
    topico = serializers.CharField(max_length=160, required=False, allow_blank=True)


class CriarMensagemSerializer(serializers.Serializer):
    conteudo = serializers.CharField(max_length=12000, trim_whitespace=True)


class ConfiguracaoTutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoTutor
        fields = [
            "estilo",
            "dificuldade",
            "foco_exame",
            "tamanho_resposta",
            "correcao_comentada",
            "foco_dificuldades",
            "resposta_audio",
            "usar_arquivos_contexto",
        ]
