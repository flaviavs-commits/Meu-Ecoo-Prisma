class LimiteDeUsoExcedidoError(Exception):
    codigo = "limite_uso_excedido"


class PercentualInvalidoError(Exception):
    codigo = "percentual_invalido"


class MotivoObrigatorioError(Exception):
    codigo = "motivo_obrigatorio"
