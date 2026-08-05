from django.db import IntegrityError, transaction
from django.contrib.auth.password_validation import validate_password

from contas.auditoria import RegistroDeAuditoria
from contas.models import Instituicao, Perfil, Usuario


class ContaTesteJaExisteError(ValueError):
    pass


@transaction.atomic
def criar_conta_teste(
    *,
    email: str,
    nome: str,
    sobrenome: str,
    instituicao: Instituicao,
    perfil: str,
    senha: str,
    ator: Usuario,
):
    """Cria uma conta academica ativa, sem privilegios administrativos, de forma atomica."""
    if not ator.is_active or not ator.is_superuser:
        raise PermissionError("Somente um superadmin ativo pode criar contas de teste.")
    if not instituicao.ativa:
        raise ValueError("A instituicao precisa estar ativa.")
    if perfil not in Perfil.values:
        raise ValueError("Perfil academico invalido.")
    usuario_para_validacao = Usuario(email=email, first_name=nome, last_name=sobrenome)
    validate_password(senha, user=usuario_para_validacao)
    try:
        conta = Usuario.objects.create_user(
            email=email.strip().lower(),
            password=senha,
            first_name=nome.strip(),
            last_name=sobrenome.strip(),
            instituicao=instituicao,
            perfil=perfil,
            ativo=True,
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )
    except IntegrityError as erro:
        raise ContaTesteJaExisteError("Ja existe uma conta com este e-mail.") from erro

    RegistroDeAuditoria.objects.create(
        ator=ator,
        acao="criar_conta_teste",
        objeto_tipo="Usuario",
        objeto_id=str(conta.pk),
        motivo=f"conta de teste {perfil} criada pelo painel de superadmin",
    )
    return conta
