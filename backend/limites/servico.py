from contextlib import contextmanager
from dataclasses import dataclass
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.db.models import Sum

from contas.auditoria import RegistroDeAuditoria
from contas.models import TipoInstituicao

from .excecoes import (
    LimiteDeUsoExcedidoError,
    MotivoObrigatorioError,
    PercentualInvalidoError,
)
from .models import (
    AssinaturaInstituicao,
    CotaUsuario,
    ConsumoIA,
    PERCENTUAL_MAXIMO,
    PlanoInstitucional,
)


@dataclass(frozen=True)
class EstadoCota:
    limite_percentual: Decimal
    consumido_percentual: Decimal
    disponivel_percentual: Decimal
    bloqueado: bool


def obter_cota(usuario):
    cota, _ = CotaUsuario.objects.get_or_create(usuario=usuario)
    return cota


def estado_cota(usuario):
    obter_cota(usuario)
    limite = limite_da_instituicao(usuario.instituicao_id)
    consumido = (
        ConsumoIA.objects.filter(usuario=usuario).aggregate(total=Sum("percentual"))["total"]
        or Decimal("0")
    )
    disponivel = limite - consumido
    return EstadoCota(
        limite_percentual=limite,
        consumido_percentual=consumido,
        disponivel_percentual=disponivel,
        bloqueado=disponivel <= 0,
    )


@contextmanager
def trava_cota(usuario):
    """Serializa o gate e o débito da mesma conta em uma transação."""
    with transaction.atomic():
        cota = obter_cota(usuario)
        CotaUsuario.objects.select_for_update().get(pk=cota.pk)
        yield


def autorizar_uso(usuario):
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
            cota = obter_cota(usuario)
            CotaUsuario.objects.select_for_update().get(pk=cota.pk)
            estado = estado_cota(usuario)
            if estado.consumido_percentual + percentual > estado.limite_percentual:
                raise LimiteDeUsoExcedidoError()
            return ConsumoIA.objects.create(
                usuario=usuario,
                instituicao=usuario.instituicao,
                referencia=referencia,
                fornecedor=fornecedor,
                modelo=modelo,
                classe_tarefa=classe_tarefa,
                percentual=percentual,
                custo_bruto=custo_bruto,
                metadados=metadados or {},
            )
    except IntegrityError:
        return ConsumoIA.objects.get(referencia=referencia)


def atualizar_plano(*, instituicao, ator, codigo, motivo):
    motivo = str(motivo or "").strip()
    if not motivo:
        raise MotivoObrigatorioError()
    if getattr(instituicao, "tipo", None) == TipoInstituicao.MANTENEDORA:
        raise ValueError("A instituição mantenedora não possui plano comercial.")
    try:
        plano = PlanoInstitucional.objects.get(codigo=codigo, ativo=True)
    except PlanoInstitucional.DoesNotExist as erro:
        raise ValueError("Plano inexistente ou inativo.") from erro
    with transaction.atomic():
        assinatura, criada = AssinaturaInstituicao.objects.select_for_update().get_or_create(
            instituicao=instituicao,
            defaults={"plano": plano},
        )
        anterior = "nenhum" if criada else assinatura.plano.codigo
        assinatura.plano = plano
        assinatura.ativa = True
        assinatura.save(update_fields=["plano", "ativa", "atualizada_em"])
        RegistroDeAuditoria.objects.create(
            ator=ator,
            acao="alterar_plano_instituicao",
            objeto_tipo="Instituicao",
            objeto_id=str(instituicao.id),
            motivo=f"{motivo} (de {anterior} para {plano.codigo})",
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
    return {
        "plano": assinatura.plano.codigo,
        "preco_por_conta": assinatura.plano.preco_por_conta,
        "limite_percentual_por_conta": assinatura.plano.limite_percentual_por_conta,
        "contas": contagem,
        "total_contas": total_contas,
        "total_mensal": assinatura.plano.preco_por_conta * total_contas,
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
