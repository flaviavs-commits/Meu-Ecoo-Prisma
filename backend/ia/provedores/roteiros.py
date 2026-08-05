"""Saidas estruturadas deterministicas para o provedor falso.

Um provedor real recebe o formato desejado junto do prompt (`response_format`,
JSON schema) e devolve JSON. O provedor falso precisa fazer o mesmo: sem isso,
todo codigo que consome saida estruturada so seria exercitado contra o provedor
de producao - e foi exatamente assim que a geracao de simulado acabou
inventando questao no lugar de ler a resposta do modelo.

O acoplamento entre quem pede e quem responde e por *nome de contrato*, uma
string declarada no fim do prompt (`[CONTRATO=nome parametro=valor]`), igual ao
que existiria com um provedor real. Contrato novo entra como uma funcao nova em
`_ROTEIROS`, sem mexer no provedor.
"""

import json
import re


DIRETIVA = re.compile(r"\[CONTRATO=(?P<nome>[a-z_]+)(?P<parametros>[^\]]*)\]")

ALTERNATIVAS = ("A", "B", "C", "D")


def resposta_para(prompt: str) -> str | None:
    """JSON deterministico do contrato declarado no prompt, ou `None`."""
    achado = DIRETIVA.search(prompt or "")
    if not achado:
        return None
    roteiro = _ROTEIROS.get(achado.group("nome"))
    if roteiro is None:
        return None
    return roteiro(_parametros(achado.group("parametros")))


def _parametros(bruto: str) -> dict[str, str]:
    return dict(par.split("=", 1) for par in bruto.split() if "=" in par)


def _simulado_json(parametros: dict[str, str]) -> str:
    quantidade = max(1, int(parametros.get("quantidade", "1")))
    questoes = []
    for ordem in range(1, quantidade + 1):
        # O gabarito gira entre as quatro letras. Um gabarito fixo faria o
        # aluno que marca sempre a mesma alternativa tirar 100%, e esse
        # percentual alimenta o progresso por materia do dashboard.
        correta = ALTERNATIVAS[(ordem - 1) % len(ALTERNATIVAS)]
        questoes.append(
            {
                "enunciado": (
                    f"Questao {ordem} gerada pelo provedor de desenvolvimento. "
                    "Substituida por conteudo real quando o provedor de producao "
                    "for habilitado."
                ),
                "alternativas": [
                    f"Alternativa {letra} da questao {ordem}" for letra in ALTERNATIVAS
                ],
                "gabarito": correta,
            }
        )
    return json.dumps({"questoes": questoes}, ensure_ascii=False)


_ROTEIROS = {"simulado_json": _simulado_json}
