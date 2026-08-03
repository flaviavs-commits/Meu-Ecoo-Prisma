from django.http import JsonResponse
from rest_framework.views import exception_handler

_CODIGO_POR_STATUS = {
    400: "validacao",
    401: "nao_autenticado",
    403: "sem_permissao",
    404: "nao_encontrado",
    405: "metodo_nao_permitido",
    409: "conflito",
    422: "regra_de_negocio",
    429: "muitas_requisicoes",
}


def tratador_de_excecao(exc, context):
    resposta = exception_handler(exc, context)
    if resposta is None:
        return None

    codigo = _CODIGO_POR_STATUS.get(resposta.status_code, "erro")
    detalhes = resposta.data if isinstance(resposta.data, (dict, list)) else None
    mensagem = (
        detalhes.get("detail") if isinstance(detalhes, dict) and "detail" in detalhes
        else "Alguns campos estao invalidos." if codigo == "validacao"
        else "Ocorreu um erro ao processar a requisicao."
    )
    if isinstance(detalhes, dict):
        detalhes = {chave: valor for chave, valor in detalhes.items() if chave != "detail"}

    resposta.data = {
        "erro": {
            "codigo": codigo,
            "mensagem": str(mensagem),
            **({"detalhes": detalhes} if detalhes else {}),
        }
    }
    return resposta


def pagina_nao_encontrada(request, exception=None):
    return JsonResponse(
        {
            "erro": {
                "codigo": "nao_encontrado",
                "mensagem": "O recurso solicitado nao existe.",
            }
        },
        status=404,
    )
