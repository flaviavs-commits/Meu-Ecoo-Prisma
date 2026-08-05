from django.db import transaction

from .auditoria import RegistroDeAuditoria


class DesativacaoNegada(ValueError):
    def __init__(self, mensagem, *, codigo="validacao"):
        super().__init__(mensagem)
        self.codigo = codigo


def _pode_desativar(ator, alvo) -> bool:
    """Quem pode desativar quem, dito de forma afirmativa.

    Antes esta regra era um `not ator.is_staff and (...)`, e `is_staff` (um
    booleano comum, marcavel pelo Django Admin - nao o superusuario)
    curto-circuitava a checagem inteira: qualquer conta com a flag desativava
    usuario de QUALQUER instituicao. O superadmin e o unico papel cross-tenant
    do produto; diretor manda so na propria instituicao.
    """
    if ator.is_superuser:
        return True
    return (
        ator.perfil == "DIRETOR"
        # `instituicao_id` e anulavel: sem esta guarda, dois usuarios sem
        # instituicao (None == None) passariam como "mesma instituicao".
        and ator.instituicao_id is not None
        and ator.instituicao_id == alvo.instituicao_id
    )


def desativar_usuario(*, alvo, ator, confirmacao, motivo):
    if confirmacao is not True:
        raise DesativacaoNegada("Confirme a acao para continuar.")
    motivo = str(motivo or "").strip()
    if not motivo:
        raise DesativacaoNegada("Informe o motivo da acao.")
    if not _pode_desativar(ator, alvo):
        raise DesativacaoNegada(
            "Usuario sem permissao para desativar este usuario.",
            codigo="sem_permissao",
        )
    if alvo.pk == ator.pk:
        raise DesativacaoNegada("O usuario atual nao pode desativar a propria conta.")

    with transaction.atomic():
        alvo.ativo = False
        alvo.is_active = False
        alvo.save(update_fields=["ativo", "is_active", "atualizado_em"])
        RegistroDeAuditoria.objects.create(
            ator=ator,
            acao="desativar_usuario",
            objeto_tipo="Usuario",
            objeto_id=str(alvo.pk),
            motivo=motivo,
        )
