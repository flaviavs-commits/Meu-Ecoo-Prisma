"""O tier ADMINISTRADOR: staff interno da Prisma, sem poder de superadmin."""
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from contas.models import (
    CODIGO_PRISMA,
    Instituicao,
    Perfil,
    TipoInstituicao,
)


@pytest.fixture
def prisma():
    return Instituicao.objects.get(codigo=CODIGO_PRISMA)


@pytest.fixture
def administrador(prisma):
    return get_user_model().objects.create_user(
        "admin@vitissouls.test", "senha", instituicao=prisma, perfil=Perfil.ADMINISTRADOR
    )


@pytest.mark.django_db
def test_a_migracao_cria_a_instituicao_interna_prisma(prisma):
    assert prisma.tipo == TipoInstituicao.PRISMA
    assert prisma.documento is None
    assert prisma.eh_interna is True


@pytest.mark.django_db
def test_administrador_e_staff_interno_mas_nao_provider(administrador):
    assert administrador.eh_administrador is True
    assert administrador.eh_staff_interno is True
    # A diferenca que sustenta o tier: alcance cross-tenant sem superusuario.
    assert administrador.eh_provider is False
    assert administrador.is_superuser is False


@pytest.mark.django_db
def test_administrador_nao_pode_ser_superadmin(administrador):
    administrador.is_superuser = True

    with pytest.raises(ValidationError):
        administrador.full_clean()


@pytest.mark.django_db
def test_administrador_precisa_morar_na_instituicao_prisma():
    escola = Instituicao.objects.create(nome="Escola X", documento="11.111.111/0001-11")
    intruso = get_user_model()(
        email="fake@escola.test", instituicao=escola, perfil=Perfil.ADMINISTRADOR
    )

    with pytest.raises(ValidationError):
        intruso.full_clean()


@pytest.mark.django_db
def test_instituicao_prisma_nao_hospeda_conta_academica(prisma):
    aluno = get_user_model()(email="aluno@prisma.test", instituicao=prisma, perfil=Perfil.ALUNO)

    with pytest.raises(ValidationError):
        aluno.full_clean()


@pytest.mark.django_db
def test_provider_continua_exigindo_superusuario_na_vitis_souls():
    vitis = Instituicao.objects.get(codigo="VITIS_SOULS")
    assert vitis.tipo == TipoInstituicao.PROVEDORA

    provider = get_user_model().objects.create_superuser("chefe@vitissouls.test", "senha-forte-123")
    assert provider.eh_provider is True
    assert provider.eh_staff_interno is True
    assert provider.eh_administrador is False
