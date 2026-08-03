from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ResultadoProvedor:
    texto: str
    tokens_entrada: int
    tokens_saida: int
    modelo: str
    custo_bruto: Decimal


class ProvedorIA(ABC):
    @abstractmethod
    def gerar(self, prompt: str, modelo: str, timeout: float = 10) -> ResultadoProvedor:
        """Executa uma chamada com limite de tempo explicito."""
