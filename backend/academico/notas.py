from decimal import Decimal

from django.db import transaction

from contas.auditoria import RegistroDeAuditoria

from .models import ConfiguracaoNota, Falta, Matricula, Nota


class AcademicoPermissaoError(Exception):
    def __init__(self, mensagem, *, codigo="sem_permissao"):
        super().__init__(mensagem)
        self.codigo = codigo


class NotaForaDaFaixaError(Exception):
    codigo = "nota_fora_da_faixa"


def lancar_nota(*, turma, disciplina, aluno, valor, avaliacao, ator):
    _validar_lancamento(turma, disciplina, aluno, ator)
    minimo, maximo = _faixa(turma.instituicao_id)
    valor = Decimal(valor)
    if valor < minimo or valor > maximo:
        raise NotaForaDaFaixaError()
    return Nota.objects.create(
        turma=turma,
        disciplina=disciplina,
        aluno=aluno,
        valor=valor,
        avaliacao=avaliacao,
        criado_por=ator,
    )


def atualizar_nota(*, nota, novo_valor, ator):
    _validar_lancamento(nota.turma, nota.disciplina, nota.aluno, ator)
    minimo, maximo = _faixa(nota.turma.instituicao_id)
    novo_valor = Decimal(novo_valor)
    if novo_valor < minimo or novo_valor > maximo:
        raise NotaForaDaFaixaError()
    valor_anterior = nota.valor
    with transaction.atomic():
        nota.valor = novo_valor
        nota.alterado_por = ator
        nota.save()
        RegistroDeAuditoria.objects.create(
            ator=ator,
            acao="alterar_nota",
            objeto_tipo="Nota",
            objeto_id=str(nota.id),
            motivo=f"valor_anterior={valor_anterior}; valor_novo={novo_valor}",
        )
    return nota


def registrar_falta(*, turma, aluno, data, ator, justificada=False, motivo=""):
    _validar_lancamento(turma, turma.disciplina, aluno, ator)
    return Falta.objects.create(
        turma=turma,
        aluno=aluno,
        data=data,
        justificada=justificada,
        motivo=motivo,
        criado_por=ator,
    )


def consultar_notas(*, usuario, aluno_alvo=None):
    if aluno_alvo and aluno_alvo.instituicao_id != usuario.instituicao_id:
        raise AcademicoPermissaoError("Recurso fora da instituicao.", codigo="fora_da_instituicao")
    if usuario.perfil == "ALUNO":
        aluno_alvo = aluno_alvo or usuario
        if aluno_alvo.id != usuario.id:
            raise AcademicoPermissaoError("Aluno so pode ver as proprias notas.")
        return Nota.objects.filter(aluno_id=usuario.id).select_related("disciplina", "turma")
    if usuario.perfil == "PROFESSOR":
        notas = Nota.objects.filter(turma__professor_responsavel_id=usuario.id)
        if aluno_alvo:
            notas = notas.filter(aluno=aluno_alvo)
        return notas.select_related("disciplina", "turma")
    if usuario.perfil == "DIRETOR":
        return Nota.objects.filter(
            aluno__instituicao_id=usuario.instituicao_id
        ).select_related("disciplina", "turma")
    raise AcademicoPermissaoError("Perfil sem acesso academico.")


def _validar_lancamento(turma, disciplina, aluno, ator):
    if any(
        objeto.instituicao_id != turma.instituicao_id
        for objeto in [aluno, disciplina]
    ) or ator.instituicao_id != turma.instituicao_id:
        raise AcademicoPermissaoError(
            "Recurso fora da instituicao.", codigo="fora_da_instituicao"
        )
    if ator.perfil == "DIRETOR":
        return
    if ator.perfil != "PROFESSOR" or turma.professor_responsavel_id != ator.id:
        raise AcademicoPermissaoError("Professor nao responsavel pela turma.")
    if not Matricula.objects.filter(turma=turma, aluno=aluno, saiu_em__isnull=True).exists():
        raise AcademicoPermissaoError("Aluno nao esta matriculado na turma.")


def _faixa(instituicao_id):
    configuracao = ConfiguracaoNota.objects.filter(instituicao_id=instituicao_id).first()
    if not configuracao:
        return Decimal("0"), Decimal("10")
    return configuracao.nota_minima, configuracao.nota_maxima
