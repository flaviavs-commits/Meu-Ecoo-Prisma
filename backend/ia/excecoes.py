class ProvedorIAError(Exception):
    """Erro seguro e normalizado vindo do provedor de IA."""

    def __init__(self, mensagem, *, codigo="erro_provedor", transitorio=False):
        super().__init__(mensagem)
        self.codigo = codigo
        self.transitorio = transitorio


class ProvedorNaoConfiguradoError(ProvedorIAError):
    def __init__(self):
        super().__init__(
            "O provedor de IA real ainda nao foi habilitado.",
            codigo="provedor_nao_configurado",
        )
