from .base import ProvedorIA, ResultadoProvedor
from ..excecoes import ProvedorNaoConfiguradoError


class ProvedorOpenRouter(ProvedorIA):
    """Esqueleto do adaptador; rede real fica fora da E06."""

    def gerar(self, prompt: str, modelo: str, timeout: float = 10) -> ResultadoProvedor:
        raise ProvedorNaoConfiguradoError()
