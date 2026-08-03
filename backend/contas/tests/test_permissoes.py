from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from contas.acoes import AcaoDestrutivaMixin
from contas.auditoria import RegistroDeAuditoria
from contas.models import Instituicao, Perfil
from contas.permissoes.e_aluno import EAluno
from contas.permissoes.e_diretor import EDiretor
from contas.permissoes.e_dono_do_objeto import EDonoDoObjeto
from contas.permissoes.e_professor import EProfessor
from contas.permissoes.instituicao import MesmaInstituicao
from contas.permissoes.escopo import EscopoInstituicaoMixin

pytestmark = pytest.mark.django_db


class ViewDeTeste(AcaoDestrutivaMixin, APIView):
    pass


class ViewComEscopo(EscopoInstituicaoMixin, GenericAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = []

    def get(self, request, *args, **kwargs):
        pessoa = self.get_object()
        return Response({"id": pessoa.id})


def pessoa(perfil, instituicao):
    return get_user_model().objects.create_user(
        email=f"{perfil.lower()}-{instituicao.id}@test.local", password="senha-segura-123",
        instituicao=instituicao, perfil=perfil, data_nascimento=date(2000, 1, 1),
    )


def request(user):
    pedido = RequestFactory().get("/api/v1/test/")
    pedido.user = user
    return pedido


def test_aluno_nao_tem_permissao_de_diretor():
    escola = Instituicao.objects.create(nome="A", documento="10.000.000/0001-10")
    assert EDiretor().has_permission(request(pessoa(Perfil.ALUNO, escola)), None) is False


def test_perfis_corretos_sao_reconhecidos():
    escola = Instituicao.objects.create(nome="A", documento="10.000.000/0001-11")
    assert EAluno().has_permission(request(pessoa(Perfil.ALUNO, escola)), None)
    assert EProfessor().has_permission(request(pessoa(Perfil.PROFESSOR, escola)), None)
    assert EDiretor().has_permission(request(pessoa(Perfil.DIRETOR, escola)), None)


def test_objeto_de_outra_instituicao_nao_passa():
    a = Instituicao.objects.create(nome="A", documento="10.000.000/0001-12")
    b = Instituicao.objects.create(nome="B", documento="10.000.000/0001-13")
    assert MesmaInstituicao().has_object_permission(request(pessoa(Perfil.PROFESSOR, a)), None, pessoa(Perfil.ALUNO, b)) is False


def test_objeto_da_mesma_instituicao_passa():
    escola = Instituicao.objects.create(nome="A", documento="10.000.000/0001-14")
    assert MesmaInstituicao().has_object_permission(request(pessoa(Perfil.PROFESSOR, escola)), None, pessoa(Perfil.ALUNO, escola))


def test_dono_do_objeto_e_reconhecido():
    escola = Instituicao.objects.create(nome="A", documento="10.000.000/0001-15")
    dono = pessoa(Perfil.ALUNO, escola)
    objeto = type("Objeto", (), {"usuario_id": dono.id})()
    assert EDonoDoObjeto().has_object_permission(request(dono), None, objeto)


def test_acao_sem_confirmacao_retorna_400():
    escola = Instituicao.objects.create(nome="A", documento="10.000.000/0001-17")
    ator = pessoa(Perfil.DIRETOR, escola)
    view = ViewDeTeste()
    view.request = view.initialize_request(APIRequestFactory().post("/remover/", {"motivo": "transferencia"}, format="json"))
    view.request.user = ator
    resposta = view.validar_confirmacao(view.request, ator)
    assert resposta.status_code == 400


def test_acao_sem_motivo_retorna_400():
    escola = Instituicao.objects.create(nome="A", documento="10.000.000/0001-18")
    ator = pessoa(Perfil.DIRETOR, escola)
    view = ViewDeTeste()
    view.request = view.initialize_request(APIRequestFactory().post("/remover/", {"confirmacao": True}, format="json"))
    view.request.user = ator
    resposta = view.validar_confirmacao(view.request, ator)
    assert resposta.status_code == 400


def test_auditoria_tem_ator_acao_e_motivo():
    escola = Instituicao.objects.create(nome="A", documento="10.000.000/0001-16")
    ator = pessoa(Perfil.DIRETOR, escola)
    registro = RegistroDeAuditoria.objects.create(ator=ator, acao="remover", objeto_tipo="Usuario", objeto_id="1", motivo="transferencia")
    assert registro.ator_id == ator.id
    assert registro.motivo == "transferencia"


def test_acao_valida_grava_auditoria():
    escola = Instituicao.objects.create(nome="A", documento="10.000.000/0001-19")
    ator = pessoa(Perfil.DIRETOR, escola)
    view = ViewDeTeste()
    view.request = view.initialize_request(
        APIRequestFactory().post(
            "/remover/", {"confirmacao": True, "motivo": "transferencia"}, format="json"
        )
    )
    view.request.user = ator

    assert view.validar_confirmacao(view.request, ator) is None
    assert RegistroDeAuditoria.objects.filter(ator=ator, motivo="transferencia").exists()


def test_recurso_de_outra_instituicao_responde_404():
    escola_a = Instituicao.objects.create(nome="A", documento="10.000.000/0001-20")
    escola_b = Instituicao.objects.create(nome="B", documento="10.000.000/0001-21")
    ator = pessoa(Perfil.PROFESSOR, escola_a)
    alvo = pessoa(Perfil.ALUNO, escola_b)
    pedido = APIRequestFactory().get(f"/usuarios/{alvo.id}/")
    from rest_framework.test import force_authenticate

    force_authenticate(pedido, user=ator)
    resposta = ViewComEscopo.as_view()(pedido, pk=alvo.id)

    assert resposta.status_code == 404
