from decimal import Decimal

from django.db import IntegrityError, transaction

from contas.auditoria import RegistroDeAuditoria
from contas.models import Instituicao, Usuario
from creditos.models import Lancamento, TipoLancamento


class InstituicaoJaExisteError(ValueError):
    pass


@transaction.atomic
def criar_instituicao(*, nome: str, documento: str, creditos_iniciais: Decimal, ator: Usuario):
    """Cria uma instituicao e, se informado, seu credito inicial de forma atomica."""
    nome_limpo = nome.strip()
    documento_limpo = documento.strip()
    if not ator.eh_mantenedor:
        raise PermissionError("Somente um mantenedor Vitis Souls ativo pode criar instituicoes.")
    if not nome_limpo or not documento_limpo:
        raise ValueError("Nome e documento da instituicao sao obrigatorios.")
    if creditos_iniciais < 0:
        raise ValueError("Creditos iniciais nao podem ser negativos.")
    if Instituicao.objects.filter(documento=documento_limpo).exists():
        raise InstituicaoJaExisteError("Ja existe uma instituicao com este documento.")

    try:
        instituicao = Instituicao.objects.create(nome=nome_limpo, documento=documento_limpo)
    except IntegrityError as erro:
        raise InstituicaoJaExisteError("Ja existe uma instituicao com este documento.") from erro

    if creditos_iniciais:
        Lancamento.objects.create(
            instituicao=instituicao,
            tipo=TipoLancamento.CREDITO,
            quantidade=creditos_iniciais,
            motivo="credito inicial da instituicao criada pelo painel",
            criado_por=ator,
        )

    RegistroDeAuditoria.objects.create(
        ator=ator,
        acao="criar_instituicao",
        objeto_tipo="Instituicao",
        objeto_id=str(instituicao.pk),
        motivo="instituicao criada pelo painel de superadmin",
    )
    return instituicao
