from django.db import transaction

from .models import Conversa, MemoriaConsolidada, Mensagem


def consolidar_conversa(conversa: Conversa, *, gateway, disciplina="", topico=""):
    mensagens = list(conversa.mensagens.order_by("criada_em", "id"))
    prompt = _prompt_de_mensagens(mensagens)
    periodo_inicio = mensagens[0].criada_em if mensagens else None
    periodo_fim = mensagens[-1].criada_em if mensagens else None
    with transaction.atomic():
        chamada, resumo = gateway.chamar(
            instituicao=conversa.aluno.instituicao,
            usuario=conversa.aluno,
            classe_tarefa="RESUMO",
            prompt=prompt,
            devolver_texto=True,
        )
        return MemoriaConsolidada.objects.create(
            aluno=conversa.aluno,
            disciplina=disciplina,
            topico=topico,
            resumo=resumo,
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
        )


def compactar_memorias(aluno, *, gateway, disciplina="", topico=""):
    memorias = list(
        MemoriaConsolidada.objects.filter(
            aluno=aluno, disciplina=disciplina, topico=topico
        ).order_by("criada_em", "id")
    )
    if not memorias:
        raise ValueError("Nao ha memorias para compactar.")
    prompt = "\n".join(memoria.resumo for memoria in memorias)
    periodos_inicio = [m.periodo_inicio for m in memorias if m.periodo_inicio]
    periodos_fim = [m.periodo_fim for m in memorias if m.periodo_fim]
    with transaction.atomic():
        _, resumo = gateway.chamar(
            instituicao=aluno.instituicao,
            usuario=aluno,
            classe_tarefa="RESUMO",
            prompt=prompt,
            devolver_texto=True,
        )
        return MemoriaConsolidada.objects.create(
            aluno=aluno,
            disciplina=disciplina,
            topico=topico,
            resumo=resumo,
            periodo_inicio=min(periodos_inicio) if periodos_inicio else None,
            periodo_fim=max(periodos_fim) if periodos_fim else None,
        )


def _prompt_de_mensagens(mensagens):
    return "\n".join(f"{mensagem.papel}: {mensagem.conteudo}" for mensagem in mensagens)
