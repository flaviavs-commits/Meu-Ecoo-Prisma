from datetime import timedelta
from decimal import Decimal

import pytest
from django.conf import settings
from django.db import connection
from django.utils import timezone

from limites.models import AssinaturaInstituicao, ConsumoIA, PlanoInstitucional
from limites.servico import estado_cota
from limites.excecoes import LimiteDeUsoExcedidoError
from ia.conversao import custo_para_percentual
from ia.excecoes import (
    ChamadaConcorrenteError,
    ProvedorIAError,
    ProvedorNaoConfiguradoError,
)
from ia.gateway import GatewayIA
from ia.models import ChamadaIA, ClasseTarefa, StatusChamada
from ia.provedores.base import ResultadoProvedor
from ia.provedores.falso import ProvedorFalso
from ia.roteamento import modelo_para_classe

pytestmark = pytest.mark.django_db


def definir_plano(usuario, limite="100"):
    plano = PlanoInstitucional.objects.get(codigo="PRISMA")
    plano.limite_percentual_por_conta = Decimal(limite)
    plano.save(update_fields=["limite_percentual_por_conta"])
    return AssinaturaInstituicao.objects.create(instituicao=usuario.instituicao, plano=plano)


def test_provedor_falso_devolve_resposta_deterministica():
    resultado = ProvedorFalso().gerar("pergunta", "modelo-teste")

    assert resultado.texto == "Resposta deterministica do provedor falso."
    assert resultado.modelo == "modelo-teste"
    assert resultado.tokens_entrada == 1
    assert resultado.tokens_saida == 1


def test_limite_zero_cria_chamada_com_erro_e_nao_debita(instituicao, aluno):
    definir_plano(aluno, "0")
    with pytest.raises(LimiteDeUsoExcedidoError) as erro:
        GatewayIA(provedor=ProvedorFalso()).chamar(
            instituicao=instituicao,
            usuario=aluno,
            classe_tarefa=ClasseTarefa.TUTORIA,
            prompt="duvida",
        )

    assert getattr(erro.value, "codigo", None) == "limite_uso_excedido"
    chamada = ChamadaIA.objects.get()
    assert chamada.status == StatusChamada.ERRO
    assert chamada.erro_codigo == "limite_uso_excedido"
    assert estado_cota(aluno).consumido_percentual == Decimal("0")


def test_saldo_positivo_conclui_e_debita(instituicao, aluno):
    definir_plano(aluno)

    chamada = GatewayIA(provedor=ProvedorFalso()).chamar(
        instituicao=instituicao,
        usuario=aluno,
        classe_tarefa=ClasseTarefa.TUTORIA,
        prompt="duvida",
    )

    assert chamada.status == StatusChamada.SUCESSO
    assert chamada.percentual_debitado > Decimal("0")
    assert ConsumoIA.objects.filter(referencia=chamada).count() == 1


def test_falha_do_provedor_marca_erro_sem_debito(instituicao, aluno):
    definir_plano(aluno)

    class ProvedorQueFalha:
        def gerar(self, prompt, modelo, timeout):
            raise ProvedorIAError("provedor indisponivel", codigo="provedor_indisponivel")

    with pytest.raises(ProvedorIAError):
        GatewayIA(provedor=ProvedorQueFalha()).chamar(
            instituicao=instituicao,
            usuario=aluno,
            classe_tarefa=ClasseTarefa.CORRECAO,
            prompt="texto",
        )

    chamada = ChamadaIA.objects.get()
    assert chamada.status == StatusChamada.ERRO
    assert chamada.erro_codigo == "provedor_indisponivel"
    assert estado_cota(aluno).consumido_percentual == Decimal("0")


def test_erro_transitorio_retried_com_teto_e_debita_uma_vez(instituicao, aluno):
    definir_plano(aluno)

    class ProvedorTransitorio:
        tentativas = 0

        def gerar(self, prompt, modelo, timeout):
            self.tentativas += 1
            if self.tentativas == 1:
                raise ProvedorIAError(
                    "temporario", codigo="provedor_temporario", transitorio=True
                )
            return ResultadoProvedor(
                texto="ok",
                tokens_entrada=1,
                tokens_saida=1,
                modelo=modelo,
                custo_bruto=Decimal("0.001"),
            )

    provedor = ProvedorTransitorio()
    chamada = GatewayIA(provedor=provedor, dormir=lambda _: None).chamar(
        instituicao=instituicao,
        usuario=aluno,
        classe_tarefa=ClasseTarefa.TUTORIA,
        prompt="pergunta",
    )

    assert chamada.status == StatusChamada.SUCESSO
    assert provedor.tentativas == 2
    assert ConsumoIA.objects.filter(referencia=chamada).count() == 1


def test_conversao_para_percentual_arredonda_sempre_para_cima():
    assert custo_para_percentual(
        Decimal("0.00100001"), custo_dolar_por_percentual=Decimal("0.001"), margem=Decimal("1")
    ) == Decimal("1.0001")


def test_classe_de_tarefa_resolve_modelo_configurado():
    assert modelo_para_classe(ClasseTarefa.TUTORIA) == settings.IA_MODELOS["TUTORIA"]


def test_retry_da_mesma_chamada_nao_duplica_debito(instituicao, aluno):
    definir_plano(aluno)
    gateway = GatewayIA(provedor=ProvedorFalso())
    chamada = gateway.chamar(
        instituicao=instituicao,
        usuario=aluno,
        classe_tarefa=ClasseTarefa.GERACAO,
        prompt="gera",
    )

    repetida = gateway.chamar(
        instituicao=instituicao,
        usuario=aluno,
        classe_tarefa=ClasseTarefa.GERACAO,
        prompt="nao deve reenviar",
        chamada=chamada,
    )

    assert repetida.pk == chamada.pk
    assert ConsumoIA.objects.filter(referencia=chamada).count() == 1


def test_prompt_nao_e_persistido_nem_logado(instituicao, aluno, caplog):
    definir_plano(aluno)
    prompt = "dado sensivel de menor que nao pode aparecer"

    chamada = GatewayIA(provedor=ProvedorFalso()).chamar(
        instituicao=instituicao,
        usuario=aluno,
        classe_tarefa=ClasseTarefa.RESUMO,
        prompt=prompt,
    )

    assert prompt not in caplog.text
    assert not hasattr(chamada, "prompt")
    assert not hasattr(chamada, "resposta")


def test_provedor_padrao_e_falso_e_openrouter_nao_faz_rede(monkeypatch):
    monkeypatch.setattr(settings, "IA_PROVEDOR", "falso")
    gateway = GatewayIA.from_settings()
    assert isinstance(gateway.provedor, ProvedorFalso)

    with pytest.raises(ProvedorNaoConfiguradoError):
        GatewayIA.openrouter().provedor.gerar("prompt", "modelo", timeout=1)


def test_chamada_que_estoura_o_limite_e_debitada_e_nao_perdida(instituicao, aluno):
    """Regressao do achado 7: recusar o debito depois de pagar o fornecedor.

    O provedor cobra caro o bastante para passar do restante do plano. Antes,
    `registrar_uso` recusava: o custo existia no fornecedor e nao existia na
    nossa contabilidade. Agora entra, deixa a conta negativa e barra a proxima.
    """
    definir_plano(aluno, "1")

    class ProvedorCaro:
        def gerar(self, prompt, modelo, timeout):
            return ResultadoProvedor(
                texto="ok",
                tokens_entrada=1,
                tokens_saida=1,
                modelo=modelo,
                custo_bruto=Decimal("0.005"),
                fornecedor="caro",
            )

    chamada = GatewayIA(provedor=ProvedorCaro()).chamar(
        instituicao=instituicao,
        usuario=aluno,
        classe_tarefa=ClasseTarefa.TUTORIA,
        prompt="pergunta",
    )

    consumo = ConsumoIA.objects.get(referencia=chamada)
    assert chamada.status == StatusChamada.SUCESSO
    assert consumo.percentual == chamada.percentual_debitado > Decimal("1")
    estado = estado_cota(aluno)
    assert estado.consumido_percentual == consumo.percentual
    assert estado.disponivel_percentual < 0
    assert estado.bloqueado is True


def test_segunda_chamada_e_recusada_depois_do_estouro(instituicao, aluno):
    definir_plano(aluno, "1")
    gateway = GatewayIA(provedor=ProvedorFalso())
    gateway.chamar(
        instituicao=instituicao,
        usuario=aluno,
        classe_tarefa=ClasseTarefa.TUTORIA,
        prompt="primeira",
    )

    with pytest.raises(LimiteDeUsoExcedidoError):
        gateway.chamar(
            instituicao=instituicao,
            usuario=aluno,
            classe_tarefa=ClasseTarefa.TUTORIA,
            prompt="segunda",
        )


def test_chamada_pendente_da_mesma_conta_recusa_a_seguinte(instituicao, aluno):
    """Regressao: sem esse teto, N chamadas simultaneas passariam pelo portao
    juntas (nenhuma debitou ainda) e o estouro seria do tamanho da concorrencia."""
    definir_plano(aluno)
    ChamadaIA.objects.create(
        instituicao=instituicao, usuario=aluno, status=StatusChamada.PENDENTE
    )

    with pytest.raises(ChamadaConcorrenteError) as erro:
        GatewayIA(provedor=ProvedorFalso()).chamar(
            instituicao=instituicao,
            usuario=aluno,
            classe_tarefa=ClasseTarefa.TUTORIA,
            prompt="concorrente",
        )

    assert erro.value.codigo == "chamada_em_andamento"
    nova = ChamadaIA.objects.order_by("-pk").first()
    assert nova.status == StatusChamada.ERRO
    assert nova.erro_codigo == "chamada_em_andamento"
    assert estado_cota(aluno).consumido_percentual == Decimal("0")


def test_chamada_pendente_abandonada_nao_trava_a_conta(instituicao, aluno):
    """Processo morto no meio da chamada nao pode bloquear a conta para sempre."""
    definir_plano(aluno)
    orfa = ChamadaIA.objects.create(
        instituicao=instituicao, usuario=aluno, status=StatusChamada.PENDENTE
    )
    ChamadaIA.objects.filter(pk=orfa.pk).update(
        criada_em=timezone.now() - timedelta(hours=1)
    )

    chamada = GatewayIA(provedor=ProvedorFalso()).chamar(
        instituicao=instituicao,
        usuario=aluno,
        classe_tarefa=ClasseTarefa.TUTORIA,
        prompt="depois da orfa",
    )

    assert chamada.status == StatusChamada.SUCESSO


def test_provedor_nao_e_chamado_dentro_de_transacao(instituicao, aluno):
    """Regressao do achado 5: a trava da cota nao pode atravessar a rede.

    Uma transacao aberta durante ate tres tentativas de HTTP segurava conexao
    do pool por dezenas de segundos por request.
    """
    definir_plano(aluno)
    observado = {}
    # A propria suite roda dentro de uma transacao, entao `in_atomic_block` e
    # sempre True aqui. O que importa e a profundidade: se o gateway tivesse
    # aberto uma transacao em volta da chamada, haveria um savepoint a mais.
    profundidade_base = len(connection.savepoint_ids)

    class ProvedorQueObserva:
        def gerar(self, prompt, modelo, timeout):
            observado["profundidade"] = len(connection.savepoint_ids)
            return ResultadoProvedor(
                texto="ok",
                tokens_entrada=1,
                tokens_saida=1,
                modelo=modelo,
                custo_bruto=Decimal("0.001"),
            )

    GatewayIA(provedor=ProvedorQueObserva()).chamar(
        instituicao=instituicao,
        usuario=aluno,
        classe_tarefa=ClasseTarefa.TUTORIA,
        prompt="pergunta",
    )

    assert observado["profundidade"] == profundidade_base
