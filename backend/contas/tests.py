from datetime import date

import pytest
from django.contrib.auth import get_user_model

from contas.models import Instituicao, ModeloDaInstituicao, Perfil


pytestmark = pytest.mark.django_db


def test_usuario_tem_perfil_e_instituicao():
    escola = Instituicao.objects.create(nome="Escola A", documento="00.000.000/0001-00")
    usuario = get_user_model().objects.create_user(
        email="aluno@escola.test",
        password="senha-segura",
        instituicao=escola,
        perfil=Perfil.ALUNO,
        data_nascimento=date(2012, 1, 1),
    )
    assert usuario.instituicao == escola
    assert usuario.e_menor is True


def test_manager_exige_escopo_explicito():
    escola_a = Instituicao.objects.create(nome="Escola A", documento="00.000.000/0001-01")
    escola_b = Instituicao.objects.create(nome="Escola B", documento="00.000.000/0001-02")
    get_user_model().objects.create_user(email="a@test", password="x", instituicao=escola_a, perfil=Perfil.DIRETOR)
    get_user_model().objects.create_user(email="b@test", password="x", instituicao=escola_b, perfil=Perfil.DIRETOR)
    assert get_user_model().objects.da_instituicao(escola_a).count() == 1
    assert get_user_model().objects.da_instituicao(escola_b).count() == 1


def test_e_menor_false_aos_dezoito_anos():
    hoje = date.today()
    usuario = get_user_model()(data_nascimento=date(hoje.year - 18, hoje.month, hoje.day))
    assert usuario.e_menor is False


def test_base_de_instituicao_e_abstrata():
    assert ModeloDaInstituicao._meta.abstract is True
