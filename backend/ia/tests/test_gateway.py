from decimal import Decimal

import pytest
from django.conf import settings

from creditos.models import Lancamento, TipoLancamento
from creditos.saldo import saldo_usuario
from ia.conversao import custo_para_creditos
from creditos.excecoes import SaldoInsuficienteError
from ia.excecoes import ProvedorIAError, ProvedorNaoConfiguradoError
from ia.gateway import GatewayIA
from ia.models import ChamadaIA, ClasseTarefa, StatusChamada
from ia.provedores.base import ResultadoProvedor
from ia.provedores.falso import ProvedorFalso
from ia.roteamento import modelo_para_classe

pytestmark = pytest.mark.django_db


def creditar(usuario, quantidade="10"):
    return Lancamento.objects.create(
        instituicao=usuario.instituicao,
        usuario=usuario,
        tipo=TipoLancamento.CREDITO,
        quantidade=Decimal(quantidade),
        motivo="carga de teste",
    )


def test_provedor_falso_devolve_resposta_deterministica():
    resultado = ProvedorFalso().gerar("pergunta", "modelo-teste")

    assert resultado.texto == "Resposta deterministica do provedor falso."
    assert resultado.modelo == "modelo-teste"
    assert resultado.tokens_entrada == 1
    assert resultado.tokens_saida == 1


def test_saldo_zero_cria_chamada_com_erro_e_nao_debita(instituicao, aluno):
    with pytest.raises(SaldoInsuficienteError) as erro:
        GatewayIA(provedor=ProvedorFalso()).chamar(
            instituicao=instituicao,
            usuario=aluno,
            classe_tarefa=ClasseTarefa.TUTORIA,
            prompt="duvida",
        )

    assert getattr(erro.value, "codigo", None) == "saldo_insuficiente"
    chamada = ChamadaIA.objects.get()
    assert chamada.status == StatusChamada.ERRO
    assert chamada.erro_codigo == "saldo_insuficiente"
    assert saldo_usuario(aluno.id) == Decimal("0")


def test_saldo_positivo_conclui_e_debita(instituicao, aluno):
    creditar(aluno)

    chamada = GatewayIA(provedor=ProvedorFalso()).chamar(
        instituicao=instituicao,
        usuario=aluno,
        classe_tarefa=ClasseTarefa.TUTORIA,
        prompt="duvida",
    )

    assert chamada.status == StatusChamada.SUCESSO
    assert chamada.creditos_debitados > Decimal("0")
    assert Lancamento.objects.filter(referencia=chamada, tipo=TipoLancamento.DEBITO).count() == 1


def test_falha_do_provedor_marca_erro_sem_debito(instituicao, aluno):
    creditar(aluno)

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
    assert saldo_usuario(aluno.id) == Decimal("10")


def test_erro_transitorio_retried_com_teto_e_debita_uma_vez(instituicao, aluno):
    creditar(aluno)

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
    assert Lancamento.objects.filter(referencia=chamada, tipo=TipoLancamento.DEBITO).count() == 1


def test_conversao_arredonda_sempre_para_cima():
    assert custo_para_creditos(
        Decimal("0.00100001"), custo_por_credito=Decimal("0.001"), margem=Decimal("1")
    ) == Decimal("1.0001")


def test_classe_de_tarefa_resolve_modelo_configurado():
    assert modelo_para_classe(ClasseTarefa.TUTORIA) == settings.IA_MODELOS["TUTORIA"]


def test_retry_da_mesma_chamada_nao_duplica_debito(instituicao, aluno):
    creditar(aluno)
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
    assert Lancamento.objects.filter(referencia=chamada, tipo=TipoLancamento.DEBITO).count() == 1


def test_prompt_nao_e_persistido_nem_logado(instituicao, aluno, caplog):
    creditar(aluno)
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
