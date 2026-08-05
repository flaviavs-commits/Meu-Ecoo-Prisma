from django.db import IntegrityError, transaction

from contas.auditoria import RegistroDeAuditoria
from contas.models import Instituicao, Usuario
from limites.models import AssinaturaInstituicao, PlanoInstitucional


class InstituicaoJaExisteError(ValueError):
    pass


@transaction.atomic
def criar_instituicao(*, nome: str, documento: str, plano: PlanoInstitucional, ator: Usuario):
    """Cria uma escola e vincula o plano cobrado por conta de forma atomica."""
    nome_limpo = nome.strip()
    documento_limpo = documento.strip()
    if not ator.eh_mantenedor:
        raise PermissionError("Somente um mantenedor Vitis Souls ativo pode criar instituicoes.")
    if not nome_limpo or not documento_limpo:
        raise ValueError("Nome e documento da instituicao sao obrigatorios.")
    if not plano or not plano.ativo:
        raise ValueError("A instituicao precisa de um plano ativo.")
    if Instituicao.objects.filter(documento=documento_limpo).exists():
        raise InstituicaoJaExisteError("Ja existe uma instituicao com este documento.")

    try:
        instituicao = Instituicao.objects.create(nome=nome_limpo, documento=documento_limpo)
    except IntegrityError as erro:
        raise InstituicaoJaExisteError("Ja existe uma instituicao com este documento.") from erro

    AssinaturaInstituicao.objects.create(instituicao=instituicao, plano=plano)

    RegistroDeAuditoria.objects.create(
        ator=ator,
        acao="criar_instituicao",
        objeto_tipo="Instituicao",
        objeto_id=str(instituicao.pk),
        motivo=f"instituicao criada com plano {plano.codigo} pelo painel de superadmin",
    )
    return instituicao
