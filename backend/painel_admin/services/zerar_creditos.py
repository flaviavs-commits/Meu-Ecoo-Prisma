from creditos.alocacao import reduzir_alocacao
from creditos.consumo import trava_saldo
from creditos.saldo import saldo_usuario


class SaldoJaZeradoError(ValueError):
    pass


def zerar_creditos_usuario(*, alvo, ator, confirmado: bool, motivo: str):
    """Zera o saldo de creditos alocado a um usuario: acao destrutiva auditada (E14/E04)."""
    # `trava_saldo` e a MESMA trava que o debito de consumo de IA usa
    # (`creditos/consumo.py`), entao ler o saldo e reduzi-lo aqui serializa
    # contra uma resposta de IA sendo debitada no mesmo instante. Sem ela, um
    # debito entre a leitura e a escrita fazia gravar um valor ja obsoleto e o
    # saldo do usuario terminava negativo.
    with trava_saldo(alvo):
        saldo = saldo_usuario(alvo.pk)
        if saldo <= 0:
            raise SaldoJaZeradoError("Usuario ja esta com saldo zerado.")
        return reduzir_alocacao(
            instituicao=alvo.instituicao,
            origem_usuario=alvo,
            quantidade=saldo,
            motivo=motivo,
            criado_por=ator,
            confirmado=confirmado,
        )
