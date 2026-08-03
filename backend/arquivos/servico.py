from django.conf import settings
from django.db import transaction
from django.db.models import Sum

from .excecoes import (
    ArquivoCotaExcedidaError,
    ArquivoTamanhoExcedidoError,
    ArquivoTipoNaoPermitidoError,
)
from .models import Arquivo, caminho_arquivo
from .storage import StorageAdapter
from .validacao import TIPOS_PERMITIDOS, detectar_mime


def enviar_arquivo(*, instituicao, enviado_por, arquivo, storage=None):
    tamanho = arquivo.size
    limite = settings.ARQUIVO_MAX_BYTES
    if tamanho > limite:
        raise ArquivoTamanhoExcedidoError()
    tipo_mime = detectar_mime(arquivo)
    if tipo_mime not in TIPOS_PERMITIDOS:
        raise ArquivoTipoNaoPermitidoError()
    usado = (
        Arquivo.objects.filter(instituicao=instituicao).aggregate(total=Sum("tamanho_bytes"))["total"]
        or 0
    )
    if usado + tamanho > settings.ARQUIVO_COTA_INSTITUICAO_BYTES:
        raise ArquivoCotaExcedidaError()

    registro = Arquivo(
        instituicao=instituicao,
        enviado_por=enviado_por,
        nome_original=arquivo.name,
        tipo_mime=tipo_mime,
        tamanho_bytes=tamanho,
    )
    storage = storage or StorageAdapter()
    nome = caminho_arquivo(registro, arquivo.name)
    nome_salvo = storage.save(nome, arquivo)
    try:
        with transaction.atomic():
            registro.arquivo.name = nome_salvo
            registro.save(force_insert=True)
    except Exception:
        storage.delete(nome_salvo)
        raise
    return registro
