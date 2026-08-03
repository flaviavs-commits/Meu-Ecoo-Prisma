from .models import ConfiguracaoAlertaSaldo
from .saldo import saldo_usuario


def estado_alerta_usuario(usuario):
    """Calcula o alerta sem persistir saldo mutavel nem disparar notificacao."""
    configuracao = ConfiguracaoAlertaSaldo.objects.filter(
        instituicao_id=usuario.instituicao_id
    ).first()
    saldo = saldo_usuario(usuario.id)
    limiar = configuracao.limiar if configuracao else None
    return {
        "saldo": saldo,
        "limiar": limiar,
        "saldo_baixo": bool(limiar is not None and saldo <= limiar),
    }
