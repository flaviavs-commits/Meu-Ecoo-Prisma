"""Ajusta um contrato de assinatura conforme a demanda observada.

Uma assinatura tem preço fixo e capacidade limitada. Quantas contas ela atende
e quantas chamadas cada conta faz por mês são estimativas, e estimativa que não
se corrige envelhece: se uma assinatura do Claude que atendia 200 contas passa
a atender 400, o rateio por chamada cai pela metade, porque a mesma
mensalidade agora se dilui no dobro do uso.

**Garantia que este módulo precisa preservar** (requisito 4): recalibrar vale
só para as chamadas seguintes. O percentual já debitado está gravado em
`ConsumoIA`, que é append-only, e nunca é recalculado. A camada do provedor
pode se mover à vontade; a porcentagem que o usuário já viu consumida não
volta atrás nem salta para frente.
"""
from django.db import transaction

from contas.auditoria import RegistroDeAuditoria

from .modalidades import Modalidade
from .models import ContratoProvedor


class RecalibracaoNegada(ValueError):
    pass


@transaction.atomic
def recalibrar_assinatura(
    *, contrato, ator, contas_atendidas=None, chamadas_por_conta_no_mes=None, motivo
):
    motivo = str(motivo or "").strip()
    if not motivo:
        raise RecalibracaoNegada("Informe o motivo da recalibração.")
    if not getattr(ator, "eh_staff_interno", False):
        raise PermissionError("Somente a equipe interna recalibra contrato de provedor.")
    if contrato.modalidade != Modalidade.ASSINATURA_RATEIO:
        # A assinatura relativa se ajusta pelo fator sobre a referência, não por
        # estimativa de capacidade — não há rateio a recalibrar nela.
        raise RecalibracaoNegada(
            "Só contrato de assinatura por rateio tem capacidade a recalibrar."
        )

    travado = ContratoProvedor.objects.select_for_update().get(pk=contrato.pk)
    anterior = (
        f"{travado.contas_atendidas} contas x "
        f"{travado.chamadas_por_conta_no_mes} chamadas "
        f"(US$ {travado.custo_por_chamada:.8f}/chamada)"
    )

    if contas_atendidas is not None:
        if contas_atendidas < 1:
            raise RecalibracaoNegada("Uma assinatura atende ao menos uma conta.")
        travado.contas_atendidas = contas_atendidas
    if chamadas_por_conta_no_mes is not None:
        if chamadas_por_conta_no_mes < 1:
            raise RecalibracaoNegada("Estimativa de chamadas precisa ser positiva.")
        travado.chamadas_por_conta_no_mes = chamadas_por_conta_no_mes
    travado.save(update_fields=["contas_atendidas", "chamadas_por_conta_no_mes", "atualizado_em"])

    RegistroDeAuditoria.objects.create(
        ator=ator,
        acao="recalibrar_contrato_provedor",
        objeto_tipo="ContratoProvedor",
        objeto_id=str(travado.pk),
        motivo=(
            f"{motivo} (de {anterior} para {travado.contas_atendidas} contas x "
            f"{travado.chamadas_por_conta_no_mes} chamadas — "
            f"US$ {travado.custo_por_chamada:.8f}/chamada)"
        ),
    )
    return travado
