from rest_framework import serializers


class ArquivoUploadSerializer(serializers.Serializer):
    arquivo = serializers.FileField()
