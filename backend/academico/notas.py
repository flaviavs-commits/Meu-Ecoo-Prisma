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


class NotaJaOficialError(Exception):
    codigo = "nota_ja_oficial"


class AcademicoConfirmacaoError(Exception):
    codigo = "confirmacao_obrigatoria"

    def __init__(self, mensagem):
        super().__init__(mensagem)


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
    era_oficial = nota.oficial
    with transaction.atomic():
        nota.valor = novo_valor
        nota.alterado_por = ator
        # Alterar o valor derruba a aprovacao: o diretor so pode enxergar numero
        # que o professor revisou, e o numero acabou de mudar. Precisa passar por
        # `aprovar_nota` de novo.
        nota.oficial = False
        nota.save()
        RegistroDeAuditoria.objects.create(
            ator=ator,
            acao="alterar_nota",
            objeto_tipo="Nota",
            objeto_id=str(nota.id),
            motivo=(
                f"valor_anterior={valor_anterior}; valor_novo={novo_valor}"
                + ("; aprovacao revogada, exige nova revisao" if era_oficial else "")
            ),
        )
    return nota


def aprovar_nota(*, nota, ator, confirmacao, motivo):
    """Professor revisa e aprova a nota: so entao ela existe para o diretor (E09/E10).

    Mesmo padrao de `conteudo.servico.oficializar_prova`: confirmacao explicita,
    motivo obrigatorio e auditoria. Ate esta acao, a nota e rascunho - trabalho
    em andamento entre aluno e professor.
    """
    with transaction.atomic():
        # Recarrega e trava antes de olhar `oficial`: caso contrario, uma
        # tentativa cross-tenant poderia distinguir nota aprovada (409) de
        # nota nao aprovada (403), e duas aprovacoes concorrentes poderiam
        # criar duas auditorias para a mesma nota.
        nota = Nota.objects.select_for_update().select_related("turma").get(pk=nota.pk)
        if nota.turma.instituicao_id != ator.instituicao_id:
            raise AcademicoPermissaoError(
                "Recurso fora da instituicao.", codigo="fora_da_instituicao"
            )
        if ator.perfil != "PROFESSOR" or nota.turma.professor_responsavel_id != ator.id:
            raise AcademicoPermissaoError("Professor nao responsavel pela turma.")
        if nota.oficial:
            raise NotaJaOficialError()
        if confirmacao is not True:
            raise AcademicoConfirmacaoError("Confirme a aprovacao da nota.")
        motivo = str(motivo or "").strip()
        if not motivo:
            raise AcademicoConfirmacaoError("Informe o motivo da aprovacao.")
        nota.oficial = True
        nota.alterado_por = ator
        nota.save(update_fields=["oficial", "alterado_por", "alterado_em"])
        RegistroDeAuditoria.objects.create(
            ator=ator,
            acao="aprovar_nota",
            objeto_tipo="Nota",
            objeto_id=str(nota.id),
            motivo=motivo,
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
    # `instituicao` e anulavel no model. Sem esta guarda, um usuario sem
    # instituicao comparado a outro tambem sem (None == None) passava como
    # "mesma instituicao", e o filtro do diretor
    # (`aluno__instituicao_id=None`) devolvia o balde inteiro de usuarios
    # orfaos como se fosse um tenant.
    if usuario.instituicao_id is None:
        raise AcademicoPermissaoError("Usuario sem instituicao.", codigo="sem_instituicao")
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
        # Diretor le a instituicao inteira, mas so o que o professor ja revisou e
        # aprovou (`oficial=True`) - nota em rascunho e trabalho em andamento
        # entre aluno e professor. Regra de produto, 2026-08-05.
        notas = Nota.objects.filter(
            aluno__instituicao_id=usuario.instituicao_id, oficial=True
        )
        # O ramo do professor ja respeitava `aluno_alvo`; este nao. Sem o filtro,
        # quem passa `aluno_alvo` para um diretor recebe a instituicao inteira.
        if aluno_alvo:
            notas = notas.filter(aluno=aluno_alvo)
        return notas.select_related("disciplina", "turma")
    raise AcademicoPermissaoError("Perfil sem acesso academico.")


def _validar_lancamento(turma, disciplina, aluno, ator):
    if any(
        objeto.instituicao_id != turma.instituicao_id
        for objeto in [aluno, disciplina]
    ) or ator.instituicao_id != turma.instituicao_id:
        raise AcademicoPermissaoError(
            "Recurso fora da instituicao.", codigo="fora_da_instituicao"
        )
    # Nota fica entre aluno e professor: o diretor nao lanca, so le o que ja foi
    # aprovado (regra de produto, 2026-08-05). Antes havia um `return` aqui para
    # DIRETOR, que alem de deixa-lo lancar ainda pulava a checagem de matricula.
    if ator.perfil != "PROFESSOR" or turma.professor_responsavel_id != ator.id:
        raise AcademicoPermissaoError("Professor nao responsavel pela turma.")
    if not Matricula.objects.filter(turma=turma, aluno=aluno, saiu_em__isnull=True).exists():
        raise AcademicoPermissaoError("Aluno nao esta matriculado na turma.")


def _faixa(instituicao_id):
    configuracao = ConfiguracaoNota.objects.filter(instituicao_id=instituicao_id).first()
    if not configuracao:
        return Decimal("0"), Decimal("10")
    return configuracao.nota_minima, configuracao.nota_maxima
