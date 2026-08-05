"""Regressao: o simulado nasce da resposta do modelo, ou nao nasce.

Antes, `gerar_simulado` descartava o texto do provedor e fabricava questoes com
enunciado generico e `gabarito="A"` em todas - o aluno marcava "A" em tudo,
tirava 100%, e esse percentual alimentava o progresso por materia do dashboard.
"""

import json
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from contas.models import Instituicao, Perfil
from conteudo.excecoes import SimuladoIndisponivelError
from conteudo.models import Simulado
from conteudo.questoes_ia import CONTRATO, interpretar_questoes, montar_prompt
from conteudo.simulados import gerar_simulado
from ia.excecoes import ProvedorIAError
from ia.gateway import GatewayIA
from ia.provedores.base import ProvedorIA, ResultadoProvedor
from ia.provedores.falso import ProvedorFalso

pytestmark = pytest.mark.django_db


def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


@pytest.fixture
def aluno(db):
    instituicao = Instituicao.objects.create(
        nome="Escola Questoes IA", documento="00.000.000/0001-82"
    )
    return get_user_model().objects.create_user(
        email="aluno-questoes-ia@teste.com",
        password="senha-segura-123",
        instituicao=instituicao,
        perfil=Perfil.ALUNO,
    )


class ProvedorComTexto(ProvedorIA):
    """Provedor de teste que devolve exatamente o texto combinado."""

    def __init__(self, texto):
        self.texto = texto

    def gerar(self, prompt, modelo, timeout=10):
        return ResultadoProvedor(
            texto=self.texto,
            tokens_entrada=1,
            tokens_saida=1,
            modelo=modelo,
            custo_bruto=Decimal("0.002"),
            fornecedor="teste",
        )


def payload(quantidade, gabaritos=None):
    gabaritos = gabaritos or ["A", "B", "C", "D"]
    return json.dumps(
        {
            "questoes": [
                {
                    "enunciado": f"Enunciado real {ordem}",
                    "alternativas": [f"opcao {letra}" for letra in "ABCD"],
                    "gabarito": gabaritos[(ordem - 1) % len(gabaritos)],
                }
                for ordem in range(1, quantidade + 1)
            ]
        }
    )


# --- o contrato do prompt ------------------------------------------------


def test_prompt_declara_o_contrato_e_a_quantidade():
    prompt = montar_prompt(
        disciplina="Historia",
        estilo="ENEM",
        quantidade=7,
        foco_dificuldades=True,
        correcao_comentada=False,
    )

    assert f"[CONTRATO={CONTRATO} quantidade=7]" in prompt


# --- o interpretador ------------------------------------------------------


def test_interpreta_questoes_do_modelo():
    questoes = interpretar_questoes(payload(4), quantidade=4)

    assert [questao.gabarito for questao in questoes] == ["A", "B", "C", "D"]
    assert questoes[0].enunciado == "Enunciado real 1"


def test_tolera_cerca_de_codigo_em_volta_do_json():
    questoes = interpretar_questoes(f"```json\n{payload(1)}\n```", quantidade=1)

    assert len(questoes) == 1


@pytest.mark.parametrize(
    "texto",
    [
        "Resposta deterministica do provedor falso.",
        "",
        "[]",
        json.dumps({"questoes": "nao e lista"}),
        json.dumps({"questoes": [{"enunciado": "", "alternativas": ["a", "b", "c", "d"], "gabarito": "A"}]}),
        json.dumps({"questoes": [{"enunciado": "ok", "alternativas": ["a", "b"], "gabarito": "A"}]}),
        json.dumps({"questoes": [{"enunciado": "ok", "alternativas": ["a", "b", "c", "d"], "gabarito": "Z"}]}),
        json.dumps({"questoes": [{"enunciado": "ok", "alternativas": ["a", "b", "c", ""], "gabarito": "A"}]}),
    ],
)
def test_saida_fora_do_contrato_recusa_o_simulado(texto):
    with pytest.raises(SimuladoIndisponivelError):
        interpretar_questoes(texto, quantidade=1)


def test_quantidade_diferente_da_pedida_recusa_o_simulado():
    with pytest.raises(SimuladoIndisponivelError):
        interpretar_questoes(payload(2), quantidade=5)


# --- o servico ------------------------------------------------------------


def test_provedor_falso_honra_o_contrato_e_varia_o_gabarito(aluno):
    simulado = gerar_simulado(
        aluno=aluno,
        disciplina="Matematica",
        quantidade=4,
        gateway=GatewayIA(provedor=ProvedorFalso()),
    )

    gabaritos = list(simulado.questoes.values_list("gabarito", flat=True))
    assert gabaritos == ["A", "B", "C", "D"]


def test_modelo_fora_do_contrato_nao_cria_simulado(aluno):
    with pytest.raises(SimuladoIndisponivelError):
        gerar_simulado(
            aluno=aluno,
            disciplina="Matematica",
            quantidade=3,
            gateway=GatewayIA(provedor=ProvedorComTexto("desculpe, nao consigo")),
        )

    assert Simulado.objects.count() == 0


def test_enunciado_vem_do_modelo_e_nao_de_texto_fabricado(aluno):
    simulado = gerar_simulado(
        aluno=aluno,
        disciplina="Geografia",
        quantidade=2,
        gateway=GatewayIA(provedor=ProvedorComTexto(payload(2))),
    )

    assert list(simulado.questoes.values_list("enunciado", flat=True)) == [
        "Enunciado real 1",
        "Enunciado real 2",
    ]


# --- a rota ---------------------------------------------------------------


def test_rota_devolve_503_quando_o_provedor_nao_entrega_questoes(aluno, monkeypatch):
    monkeypatch.setattr(
        GatewayIA, "from_settings", classmethod(lambda cls: cls(ProvedorComTexto("nada util")))
    )

    resposta = cliente(aluno).post(
        "/api/v1/conteudo/simulados/gerar/",
        {"disciplina": "Fisica", "quantidade": 2},
        format="json",
    )

    assert resposta.status_code == 503
    assert resposta.data["erro"]["codigo"] == "simulado_indisponivel"
    assert Simulado.objects.count() == 0


def test_rota_devolve_503_quando_o_provedor_nao_esta_configurado(aluno, monkeypatch):
    class ProvedorQuebrado(ProvedorIA):
        def gerar(self, prompt, modelo, timeout=10):
            raise ProvedorIAError("indisponivel", codigo="erro_provedor")

    monkeypatch.setattr(
        GatewayIA, "from_settings", classmethod(lambda cls: cls(ProvedorQuebrado()))
    )

    resposta = cliente(aluno).post(
        "/api/v1/conteudo/simulados/gerar/",
        {"disciplina": "Fisica", "quantidade": 1},
        format="json",
    )

    assert resposta.status_code == 503
    assert resposta.data["erro"]["codigo"] == "erro_provedor"
