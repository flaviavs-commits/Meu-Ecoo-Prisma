from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class LoginSerializer(TokenObtainPairSerializer):
    username_field = "email"

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["perfil"] = user.perfil
        token["instituicao_id"] = user.instituicao_id
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["refresh"] = data.pop("refresh")
        return data


class EuSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nome = serializers.CharField(source="get_full_name")
    perfil = serializers.CharField()
    instituicao_id = serializers.IntegerField(allow_null=True)
