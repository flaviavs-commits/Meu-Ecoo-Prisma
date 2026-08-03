from rest_framework import serializers

from .models import Conversa, Mensagem


class MensagemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensagem
        fields = ["id", "papel", "conteudo", "criada_em"]
        read_only_fields = fields


class ConversaSerializer(serializers.ModelSerializer):
    mensagens = MensagemSerializer(many=True, read_only=True)

    class Meta:
        model = Conversa
        fields = ["id", "titulo", "criada_em", "mensagens"]
        read_only_fields = fields
