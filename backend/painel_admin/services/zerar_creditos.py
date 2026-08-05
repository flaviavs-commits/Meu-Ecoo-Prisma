from creditos.alocacao import reduzir_alocacao
from creditos.excecoes import AlocacaoSemConfirmacaoError
from creditos.saldo import saldo_usuario


class SaldoJaZeradoError(ValueError):
    pass


def zerar_creditos_usuario(*, alvo, ator, confirmado: bool, motivo: str):
    """Zera o saldo de creditos alocado a um usuario: acao destrutiva auditada (E14/E04)."""
    saldo = saldo_usuario(alvo.pk)
    if saldo <= 0:
        raise SaldoJaZeradoError("Usuario ja esta com saldo zerado.")
    try:
        return reduzir_alocacao(
            instituicao=alvo.instituicao,
            origem_usuario=alvo,
            quantidade=saldo,
            motivo=motivo,
            criado_por=ator,
            confirmado=confirmado,
        )
    except AlocacaoSemConfirmacaoError as erro:
        raise AlocacaoSemConfirmacaoError(str(erro)) from erro
