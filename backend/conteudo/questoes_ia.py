"""Contrato de saida estruturada entre o gateway de IA e o simulado.

Antes, `gerar_simulado` chamava o modelo, descartava a resposta e fabricava
questoes com enunciado generico e `gabarito="A"` em todas. O aluno marcava "A"
em tudo, tirava 100%, e esse percentual alimentava o progresso por materia do
dashboard - dado falso, pago com chamada de IA real.

Aqui o texto do modelo e a unica fonte das questoes. Se o provedor nao honrar o
contrato, o simulado nao nasce: e melhor uma falha explicita do que um simulado
que parece valido e nao e.
"""

import json
from dataclasses import dataclass

from .excecoes import SimuladoIndisponivelError


CONTRATO = "simulado_json"
ALTERNATIVAS = ("A", "B", "C", "D")


@dataclass(frozen=True)
class QuestaoGerada:
    enunciado: str
    alternativas: list[str]
    gabarito: str


def montar_prompt(
    *, disciplina, estilo, quantidade, foco_dificuldades, correcao_comentada
) -> str:
    """Prompt com o formato de resposta exigido declarado de forma explicita."""
    return "\n".join(
        [
            f"Gere {quantidade} questoes de multipla escolha de {disciplina} "
            f"no estilo {estilo}.",
            f"Priorizar as dificuldades recentes do aluno: {'sim' if foco_dificuldades else 'nao'}.",
            f"Incluir correcao comentada: {'sim' if correcao_comentada else 'nao'}.",
            "",
            "Responda SOMENTE com um objeto JSON valido, sem cercas de codigo,"
            ' no formato: {"questoes": [{"enunciado": "...", "alternativas":'
            ' ["...", "...", "...", "..."], "gabarito": "A"}]}.',
            f"Sao exatamente {quantidade} questoes, cada uma com exatamente "
            f"{len(ALTERNATIVAS)} alternativas, e o gabarito e uma das letras "
            f"{', '.join(ALTERNATIVAS)}.",
            f"[CONTRATO={CONTRATO} quantidade={quantidade}]",
        ]
    )


def interpretar_questoes(texto, *, quantidade) -> list[QuestaoGerada]:
    """Le a resposta do modelo, ou recusa o simulado inteiro.

    Levanta `SimuladoIndisponivelError` em qualquer desvio do contrato: nao ha
    conserto parcial que nao vire questao inventada.
    """
    dados = _json_do_modelo(texto)
    questoes = dados.get("questoes")
    if not isinstance(questoes, list):
        raise SimuladoIndisponivelError("A resposta do modelo nao trouxe questoes.")
    if len(questoes) != quantidade:
        raise SimuladoIndisponivelError(
            f"O modelo devolveu {len(questoes)} questoes; foram pedidas {quantidade}."
        )
    return [_questao(bruta, ordem) for ordem, bruta in enumerate(questoes, start=1)]


def _json_do_modelo(texto):
    try:
        dados = json.loads(_sem_cerca(texto))
    except (TypeError, ValueError) as erro:
        raise SimuladoIndisponivelError(
            "A resposta do modelo nao e um JSON valido."
        ) from erro
    if not isinstance(dados, dict):
        raise SimuladoIndisponivelError("A resposta do modelo nao e um objeto JSON.")
    return dados


def _sem_cerca(texto):
    """Tolera a cerca de codigo que varios modelos colocam em volta do JSON."""
    limpo = str(texto or "").strip()
    if not limpo.startswith("```"):
        return limpo
    corpo = limpo.split("\n", 1)[-1]
    return corpo.rsplit("```", 1)[0].strip()


def _questao(bruta, ordem):
    if not isinstance(bruta, dict):
        raise SimuladoIndisponivelError(f"Questao {ordem} nao e um objeto JSON.")
    enunciado = str(bruta.get("enunciado") or "").strip()
    if not enunciado:
        raise SimuladoIndisponivelError(f"Questao {ordem} veio sem enunciado.")
    alternativas = bruta.get("alternativas")
    if not isinstance(alternativas, list) or len(alternativas) != len(ALTERNATIVAS):
        raise SimuladoIndisponivelError(
            f"Questao {ordem} precisa de {len(ALTERNATIVAS)} alternativas."
        )
    alternativas = [str(alternativa or "").strip() for alternativa in alternativas]
    if not all(alternativas):
        raise SimuladoIndisponivelError(f"Questao {ordem} tem alternativa vazia.")
    gabarito = str(bruta.get("gabarito") or "").strip().upper()
    if gabarito not in ALTERNATIVAS:
        raise SimuladoIndisponivelError(
            f"Questao {ordem} tem gabarito fora de {', '.join(ALTERNATIVAS)}."
        )
    return QuestaoGerada(enunciado=enunciado, alternativas=alternativas, gabarito=gabarito)
