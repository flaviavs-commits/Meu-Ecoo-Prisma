class ProvedorIAError(Exception):
    """Erro seguro e normalizado vindo do provedor de IA."""

    def __init__(self, mensagem, *, codigo="erro_provedor", transitorio=False):
        super().__init__(mensagem)
        self.codigo = codigo
        self.transitorio = transitorio


class ChamadaConcorrenteError(Exception):
    """A conta ja tem uma chamada de IA em andamento.

    Limita a uma chamada por conta de cada vez. Sem esse teto, varias chamadas
    simultaneas passariam pelo portao de limite ao mesmo tempo (o portao le o
    consumido, e nenhuma delas ainda debitou) e o estouro do plano seria do
    tamanho da concorrencia. Com ele, o estouro maximo e uma chamada.
    """

    codigo = "chamada_em_andamento"


class ProvedorNaoConfiguradoError(ProvedorIAError):
    def __init__(self):
        super().__init__(
            "O provedor de IA real ainda nao foi habilitado.",
            codigo="provedor_nao_configurado",
        )
