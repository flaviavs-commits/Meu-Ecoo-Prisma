class ArquivoError(Exception):
    codigo = "arquivo_invalido"


class ArquivoTipoNaoPermitidoError(ArquivoError):
    codigo = "tipo_arquivo_nao_permitido"


class ArquivoTamanhoExcedidoError(ArquivoError):
    codigo = "tamanho_arquivo_excedido"


class ArquivoCotaExcedidaError(ArquivoError):
    codigo = "cota_instituicao_excedida"
