"""Arquivamento e desarquivamento de instituicao.

O arquivamento desativa em massa todas as contas da escola. Antes ele gravava
uma unica auditoria, para a instituicao, e nenhuma para as contas - entao
depois do ato ninguem sabia *quais* contas estavam ativas antes dele, e nao
havia como desfazer: reativar tudo ressuscitaria tambem quem tinha sido
desativado individualmente antes, por outro motivo.

Agora cada conta atingida gera seu proprio registro de auditoria, e e ele que
torna a operacao reversivel: `desarquivar_instituicao` reativa exatamente o
conjunto do ultimo arquivamento, e nada alem dele.
"""

from django.db import transaction
from django.utils import timezone

from contas.auditoria import RegistroDeAuditoria
from contas.models import Instituicao, TipoInstituicao, Usuario


class ArquivamentoInstituicaoNegado(ValueError):
    pass


ACAO_ARQUIVAR = "arquivar_instituicao"
ACAO_DESARQUIVAR = "desarquivar_instituicao"
ACAO_DESATIVAR_CONTA = "desativar_conta_por_arquivamento"
ACAO_REATIVAR_CONTA = "reativar_conta_por_desarquivamento"


@transaction.atomic
def arquivar_instituicao(*, alvo: Instituicao, ator: Usuario, confirmado: bool, motivo: str):
    motivo = _validar(alvo=alvo, ator=ator, confirmado=confirmado, motivo=motivo)
    if not alvo.ativa:
        raise ArquivamentoInstituicaoNegado("A instituição já está arquivada.")

    # Materializa a lista ANTES do update: e ela que permite desfazer depois.
    atingidas = list(
        Usuario.objects.filter(instituicao=alvo, is_active=True).values_list("pk", flat=True)
    )
    agora = timezone.now()
    alvo.ativa = False
    alvo.save(update_fields=["ativa", "atualizado_em"])
    # `update()` nao dispara `auto_now`, entao `atualizado_em` vai na mao.
    Usuario.objects.filter(pk__in=atingidas).update(
        ativo=False, is_active=False, atualizado_em=agora
    )
    _auditar(
        ator=ator,
        alvo=alvo,
        motivo=motivo,
        acao_instituicao=ACAO_ARQUIVAR,
        acao_conta=ACAO_DESATIVAR_CONTA,
        contas=atingidas,
    )
    return alvo


@transaction.atomic
def desarquivar_instituicao(*, alvo: Instituicao, ator: Usuario, confirmado: bool, motivo: str):
    """Reativa a instituicao e exatamente as contas que o arquivamento derrubou."""
    motivo = _validar(alvo=alvo, ator=ator, confirmado=confirmado, motivo=motivo)
    if alvo.ativa:
        raise ArquivamentoInstituicaoNegado("A instituição já está ativa.")

    agora = timezone.now()
    alvo.ativa = True
    alvo.save(update_fields=["ativa", "atualizado_em"])
    # `instituicao=alvo` no filtro: conta transferida para outra escola depois
    # do arquivamento nao volta por este caminho.
    reativadas = list(
        Usuario.objects.filter(
            pk__in=_contas_do_ultimo_arquivamento(alvo), instituicao=alvo
        ).values_list("pk", flat=True)
    )
    Usuario.objects.filter(pk__in=reativadas).update(
        ativo=True, is_active=True, atualizado_em=agora
    )
    _auditar(
        ator=ator,
        alvo=alvo,
        motivo=motivo,
        acao_instituicao=ACAO_DESARQUIVAR,
        acao_conta=ACAO_REATIVAR_CONTA,
        contas=reativadas,
    )
    return alvo


def _validar(*, alvo, ator, confirmado, motivo):
    if not ator.eh_mantenedor:
        raise PermissionError("Somente um mantenedor Vitis Souls pode arquivar instituições.")
    if alvo.tipo == TipoInstituicao.MANTENEDORA:
        raise ArquivamentoInstituicaoNegado("A instituição Vitis Souls não pode ser arquivada.")
    if not confirmado:
        raise ArquivamentoInstituicaoNegado("Confirme a ação para continuar.")
    motivo = str(motivo or "").strip()
    if not motivo:
        raise ArquivamentoInstituicaoNegado("Informe o motivo da ação.")
    return motivo


def _contas_do_ultimo_arquivamento(alvo):
    """PKs desativadas pelo arquivamento mais recente desta instituicao.

    Recortar pelo ultimo arquivamento importa: entre um ciclo e outro alguem
    pode ter sido desativado individualmente, e essa conta nao pode voltar
    junto so porque a escola foi reaberta.
    """
    ultimo = (
        RegistroDeAuditoria.objects.filter(
            acao=ACAO_ARQUIVAR, objeto_tipo="Instituicao", objeto_id=str(alvo.pk)
        )
        .order_by("-criado_em", "-id")
        .first()
    )
    if ultimo is None:
        return []
    return [
        int(registro.objeto_id)
        for registro in RegistroDeAuditoria.objects.filter(
            acao=ACAO_DESATIVAR_CONTA,
            objeto_tipo="Usuario",
            criado_em__gte=ultimo.criado_em,
            motivo__startswith=_prefixo_motivo(alvo),
        )
    ]


def _prefixo_motivo(alvo):
    """Marca que amarra o registro da conta ao arquivamento de uma escola."""
    return f"[instituicao={alvo.pk}] "


def _auditar(*, ator, alvo, motivo, acao_instituicao, acao_conta, contas):
    RegistroDeAuditoria.objects.create(
        ator=ator,
        acao=acao_instituicao,
        objeto_tipo="Instituicao",
        objeto_id=str(alvo.pk),
        motivo=f"{motivo} ({len(contas)} contas afetadas)",
    )
    # Um registro por conta: e o que diz, depois do ato, quais contas o
    # arquivamento derrubou - e o que torna o desarquivamento possivel.
    RegistroDeAuditoria.objects.bulk_create(
        RegistroDeAuditoria(
            ator=ator,
            acao=acao_conta,
            objeto_tipo="Usuario",
            objeto_id=str(pk),
            motivo=f"{_prefixo_motivo(alvo)}{motivo}",
        )
        for pk in contas
    )
