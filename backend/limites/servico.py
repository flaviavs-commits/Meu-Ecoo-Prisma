from contextlib import contextmanager
from dataclasses import dataclass
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.db.models import Sum

from contas.auditoria import RegistroDeAuditoria
from contas.models import TIPOS_INTERNOS, TipoInstituicao

from .ciclo import ciclo_atual
from .excecoes import (
    LimiteDeUsoExcedidoError,
    MotivoObrigatorioError,
    PercentualInvalidoError,
)
from .models import (
    AssinaturaInstituicao,
    Periodicidade,
    CotaUsuario,
    ConsumoIA,
    PERCENTUAL_MAXIMO,
    PlanoInstitucional,
)


@dataclass(frozen=True)
class EstadoCota:
    ciclo: str
    limite_percentual: Decimal
    consumido_percentual: Decimal
    disponivel_percentual: Decimal
    bloqueado: bool


def obter_cota(usuario):
    cota, _ = CotaUsuario.objects.get_or_create(usuario=usuario)
    return cota


def estado_cota(usuario, *, ciclo=None):
    """Situacao da conta dentro de uma competencia mensal.

    O plano e cobrado por conta/mes, entao o consumido e sempre o da janela
    aberta - somar o historico inteiro deixaria a conta bloqueada para sempre
    depois do primeiro mes cheio, com a escola sendo cobrada de novo.
    """
    ciclo = ciclo or ciclo_atual()
    obter_cota(usuario)
    # O limite e o mesmo para todas as contas da instituicao: quem contrata e a
    # escola, e o plano vale igual para aluno, professor e diretor. Nao existe
    # cota nominal, para mais nem para menos.
    limite = limite_da_instituicao(usuario.instituicao_id)
    consumido = (
        ConsumoIA.objects.filter(usuario=usuario, ciclo=ciclo).aggregate(
            total=Sum("percentual")
        )["total"]
        or Decimal("0")
    )
    disponivel = limite - consumido
    return EstadoCota(
        ciclo=ciclo,
        limite_percentual=limite,
        consumido_percentual=consumido,
        disponivel_percentual=disponivel,
        bloqueado=disponivel <= 0,
    )


@contextmanager
def trava_cota(usuario):
    """Serializa as decisoes de portao da mesma conta.

    Segura a linha de `CotaUsuario` para que duas requisicoes da mesma conta
    nao decidam ao mesmo tempo se podem comecar uma chamada. E deliberadamente
    curta: nenhuma chamada de rede pode acontecer aqui dentro, senao a
    transacao fica aberta pelo tempo do provedor.
    """
    with transaction.atomic():
        cota = obter_cota(usuario)
        CotaUsuario.objects.select_for_update().get(pk=cota.pk)
        yield


def autorizar_uso(usuario):
    """Portao: decide se a conta pode *comecar* mais uma chamada.

    E o unico ponto que recusa. Depois que o provedor foi acionado, o custo ja
    existe e `registrar_uso` sempre grava - ver a nota la.
    """
    estado = estado_cota(usuario)
    if estado.disponivel_percentual <= 0:
        raise LimiteDeUsoExcedidoError()
    return estado


def registrar_uso(
    *,
    usuario,
    percentual,
    fornecedor,
    modelo,
    classe_tarefa,
    referencia,
    custo_bruto=Decimal("0"),
    metadados=None,
):
    """Grava o consumo de uma chamada ja concluida. Nunca recusa.

    Este e o livro-razao: o percentual so chega aqui depois que o provedor
    respondeu, ou seja, depois que o custo virou fato. Antes, uma chamada que
    ultrapassasse o restante do plano era recusada aqui - o fornecedor cobrava,
    a nossa contabilidade nao registrava nada, e o dinheiro sumia em silencio.

    Quem decide se a conta pode comecar uma chamada e `autorizar_uso`. Como o
    gateway so deixa uma chamada por conta correr de cada vez, o estouro
    maximo de um plano e uma unica chamada, e ela bloqueia a proxima.
    """
    percentual = _percentual_positivo(percentual)
    if not fornecedor or not modelo or not classe_tarefa:
        raise ValueError("Fornecedor, modelo e classe da tarefa sao obrigatorios.")
    try:
        with transaction.atomic():
            existente = ConsumoIA.objects.filter(referencia=referencia).first()
            if existente:
                if existente.usuario_id != usuario.id:
                    raise ValueError("A chamada de IA pertence a outra conta.")
                return existente
            return ConsumoIA.objects.create(
                usuario=usuario,
                instituicao=usuario.instituicao,
                referencia=referencia,
                fornecedor=fornecedor,
                modelo=modelo,
                classe_tarefa=classe_tarefa,
                ciclo=ciclo_atual(),
                percentual=percentual,
                custo_bruto=custo_bruto,
                metadados=metadados or {},
            )
    except IntegrityError:
        return ConsumoIA.objects.get(referencia=referencia)


def atualizar_plano(*, instituicao, ator, codigo, motivo, periodicidade=None):
    motivo = str(motivo or "").strip()
    if not motivo:
        raise MotivoObrigatorioError()
    if getattr(instituicao, "tipo", None) in TIPOS_INTERNOS:
        raise ValueError("Instituição interna da equipe não possui plano comercial.")
    try:
        plano = PlanoInstitucional.objects.get(codigo=codigo, ativo=True)
    except PlanoInstitucional.DoesNotExist as erro:
        raise ValueError("Plano inexistente ou inativo.") from erro
    if periodicidade is not None and periodicidade not in Periodicidade.values:
        raise ValueError("Periodicidade inexistente: use MENSAL ou ANUAL.")
    with transaction.atomic():
        assinatura, criada = AssinaturaInstituicao.objects.select_for_update().get_or_create(
            instituicao=instituicao,
            defaults={"plano": plano},
        )
        anterior = "nenhum" if criada else f"{assinatura.plano.codigo}/{assinatura.periodicidade}"
        assinatura.plano = plano
        # Omitir a periodicidade mantem a vigente: trocar de plano no meio do
        # contrato nao deve, sozinho, rebaixar uma assinatura anual para mensal.
        if periodicidade is not None:
            assinatura.periodicidade = periodicidade
        assinatura.ativa = True
        assinatura.save(update_fields=["plano", "periodicidade", "ativa", "atualizada_em"])
        RegistroDeAuditoria.objects.create(
            ator=ator,
            acao="alterar_plano_instituicao",
            objeto_tipo="Instituicao",
            objeto_id=str(instituicao.id),
            motivo=f"{motivo} (de {anterior} para {plano.codigo}/{assinatura.periodicidade})",
        )
    return assinatura


def limite_da_instituicao(instituicao_id):
    assinatura = (
        AssinaturaInstituicao.objects.select_related("plano")
        .filter(instituicao_id=instituicao_id, ativa=True, plano__ativo=True)
        .first()
    )
    if assinatura:
        return assinatura.plano.limite_percentual_por_conta
    return Decimal("100")


def planos_disponiveis():
    return PlanoInstitucional.objects.filter(ativo=True).order_by("preco_por_conta")


def calcular_cobranca(instituicao):
    assinatura = AssinaturaInstituicao.objects.select_related("plano").get(
        instituicao=instituicao, ativa=True
    )
    contagem = {
        perfil: instituicao.usuarios.filter(ativo=True, is_active=True, perfil=perfil).count()
        for perfil in ("ALUNO", "PROFESSOR", "DIRETOR")
    }
    total_contas = sum(contagem.values())
    total_mensal = assinatura.plano.preco_por_conta * total_contas
    return {
        "plano": assinatura.plano.codigo,
        "periodicidade": assinatura.periodicidade,
        "preco_por_conta": assinatura.plano.preco_por_conta,
        "limite_percentual_por_conta": assinatura.plano.limite_percentual_por_conta,
        "contas": contagem,
        "total_contas": total_contas,
        "total_mensal": total_mensal,
        # Valor da fatura no intervalo contratado: o anual cobre doze meses de
        # uso, mesmo que a apuracao do consumo continue mes a mes.
        "total_por_cobranca": (
            total_mensal * 12
            if assinatura.periodicidade == Periodicidade.ANUAL
            else total_mensal
        ),
    }


def _percentual_positivo(valor):
    valor = _decimal(valor)
    if valor <= 0 or valor > PERCENTUAL_MAXIMO:
        raise PercentualInvalidoError()
    return valor


def _decimal(valor):
    try:
        return Decimal(str(valor))
    except (TypeError, ValueError, ArithmeticError) as erro:
        raise PercentualInvalidoError() from erro
