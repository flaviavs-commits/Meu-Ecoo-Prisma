from decimal import Decimal

import pytest
from django.conf import settings

from limites.models import AssinaturaInstituicao, ConsumoIA, PlanoInstitucional
from limites.servico import estado_cota
from limites.excecoes import LimiteDeUsoExcedidoError
from ia.conversao import custo_para_percentual
from ia.excecoes import ProvedorIAError, ProvedorNaoConfiguradoError
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
