from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from contas.models import Instituicao, Perfil, TipoInstituicao


@pytest.mark.django_db
def test_usuario_rejeita_email_duplicado_entre_instituicoes():
    primeira = Instituicao.objects.create(nome="Escola A", documento="00.000.000/0001-01")
    segunda = Instituicao.objects.create(nome="Escola B", documento="00.000.000/0001-02")
    usuario_model = get_user_model()
    aluno_a = usuario_model.objects.create_user(
        "aluno@escola.test", "senha", instituicao=primeira, perfil=Perfil.ALUNO
    )
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            usuario_model.objects.create_user(
                "aluno@escola.test", "senha", instituicao=segunda, perfil=Perfil.ALUNO
            )

    assert aluno_a.email == "aluno@escola.test"
    assert usuario_model.objects.filter(instituicao=primeira).count() == 1
    assert usuario_model.objects.filter(instituicao=segunda).count() == 0


@pytest.mark.django_db
def test_e_menor_considera_aniversario():
    hoje = date.today()
    usuario = get_user_model()(data_nascimento=hoje.replace(year=hoje.year - 18))
    assert usuario.e_menor is False
    usuario.data_nascimento = hoje.replace(year=hoje.year - 18) + timedelta(days=1)
    assert usuario.e_menor is True


@pytest.mark.django_db
def test_mantenedora_exige_o_codigo_reservado_da_vitis_souls():
    mantenedora = Instituicao(
        nome="Outra Mantenedora",
        tipo=TipoInstituicao.MANTENEDORA,
        documento=None,
        codigo="OUTRA",
    )

    with pytest.raises(ValidationError):
        mantenedora.full_clean()

    vitis = Instituicao(
        nome="Vitis Souls",
        tipo=TipoInstituicao.MANTENEDORA,
        documento=None,
        codigo="VITIS_SOULS",
    )
    vitis.full_clean()
