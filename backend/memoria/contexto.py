from .models import MemoriaConsolidada, Mensagem


def recuperar_contexto(
    aluno,
    *,
    disciplina="",
    topico="",
    conversa=None,
    limite_mensagens=8,
    limite_tokens=1200,
):
    memorias = MemoriaConsolidada.objects.filter(aluno=aluno)
    if disciplina:
        memorias = memorias.filter(disciplina=disciplina)
    if topico:
        memorias = memorias.filter(topico=topico)
    memoria_blocos = [memoria.resumo for memoria in memorias]
    mensagem_blocos = []
    if conversa:
        mensagem_blocos = list(
            Mensagem.objects.filter(conversa=conversa)
            .order_by("-criada_em", "-id")[:limite_mensagens]
        )
        mensagem_blocos.reverse()
        mensagem_blocos = [f"{mensagem.papel}: {mensagem.conteudo}" for mensagem in mensagem_blocos]
    memoria_texto = _dentro_do_orcamento(memoria_blocos, limite_tokens)
    tokens_memoria = _tokens_estimados(memoria_texto)
    mensagens_texto = _dentro_do_orcamento(
        mensagem_blocos, max(limite_tokens - tokens_memoria, 0)
    )
    texto = "\n".join(bloco for bloco in [memoria_texto, mensagens_texto] if bloco)
    return {
        "memorias": memoria_texto,
        "mensagens": mensagens_texto,
        "texto": texto,
        "tokens_estimados": _tokens_estimados(texto),
    }


def _dentro_do_orcamento(blocos, limite_tokens):
    limite_caracteres = max(limite_tokens, 0) * 4
    resultado = []
    usados = 0
    for bloco in blocos:
        if usados + len(bloco) > limite_caracteres:
            break
        resultado.append(bloco)
        usados += len(bloco) + (1 if resultado else 0)
    return "\n".join(resultado)


def _tokens_estimados(texto):
    return (len(texto) + 3) // 4
