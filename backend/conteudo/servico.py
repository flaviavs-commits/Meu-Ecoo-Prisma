from django.db import transaction
from django.utils import timezone

from contas.auditoria import RegistroDeAuditoria

from .excecoes import (
    ConteudoConflitoError,
    ConteudoConfirmacaoError,
    ConteudoForaDaInstituicaoError,
    ConteudoPermissaoError,
    ConteudoSemQuestoesError,
)
from .models import Material, OrigemConteudo, Prova, Questao, StatusConteudo


def criar_prova(*, instituicao, turma, disciplina, autor, titulo, origem=OrigemConteudo.MANUAL):
    _mesma_instituicao(instituicao, turma, disciplina, autor)
    return Prova.objects.create(
        instituicao=instituicao,
        turma=turma,
        disciplina=disciplina,
        autor=autor,
        titulo=titulo,
        origem=origem,
        status=StatusConteudo.RASCUNHO,
    )


def criar_material(*, instituicao, turma, disciplina, autor, titulo, origem=OrigemConteudo.MANUAL, arquivo=None):
    _mesma_instituicao(instituicao, turma, disciplina, autor, permitir_nulos=True)
    return Material.objects.create(
        instituicao=instituicao,
        turma=turma,
        disciplina=disciplina,
        autor=autor,
        titulo=titulo,
        origem=origem,
        arquivo=arquivo,
        status=StatusConteudo.RASCUNHO,
    )


def adicionar_questao(*, prova, enunciado, gabarito, alternativas=None, ordem=None):
    ordem = ordem or prova.questoes.count() + 1
    return Questao.objects.create(
        prova=prova,
        ordem=ordem,
        enunciado=enunciado,
        gabarito=gabarito,
        alternativas=alternativas or [],
    )


def oficializar_prova(*, prova, ator, confirmacao, motivo):
    if prova.status == StatusConteudo.OFICIAL:
        raise ConteudoConflitoError()
    if prova.instituicao_id != ator.instituicao_id:
        raise ConteudoForaDaInstituicaoError()
    if ator.perfil != "DIRETOR" and prova.autor_id != ator.id:
        raise ConteudoPermissaoError()
    if confirmacao is not True:
        raise ConteudoConfirmacaoError("Confirme a oficializacao.")
    motivo = str(motivo or "").strip()
    if not motivo:
        raise ConteudoConfirmacaoError("Informe o motivo da oficializacao.")
    if not prova.questoes.exists():
        raise ConteudoSemQuestoesError()
    with transaction.atomic():
        prova.status = StatusConteudo.OFICIAL
        prova.revisado_por = ator
        prova.revisado_em = timezone.now()
        prova._permitir_oficializacao = True
        prova.save()
        RegistroDeAuditoria.objects.create(
            ator=ator,
            acao="oficializar_prova",
            objeto_tipo="Prova",
            objeto_id=str(prova.id),
            motivo=motivo,
        )
    return prova


def _mesma_instituicao(instituicao, turma, disciplina, autor, permitir_nulos=False):
    objetos = [turma, disciplina, autor]
    if not permitir_nulos and any(objeto is None for objeto in objetos):
        raise ConteudoForaDaInstituicaoError()
    if any(objeto is not None and objeto.instituicao_id != instituicao.id for objeto in objetos):
        raise ConteudoForaDaInstituicaoError()
