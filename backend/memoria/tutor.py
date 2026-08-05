from django.db import transaction

from ia.gateway import GatewayIA
from .contexto import recuperar_contexto
from .models import ConfiguracaoTutor, Conversa, Mensagem, PapelMensagem


def criar_conversa(*, aluno, titulo="", disciplina="", topico=""):
    return Conversa.objects.create(
        aluno=aluno,
        titulo=str(titulo or "").strip()[:200],
        disciplina=str(disciplina or "").strip()[:120],
        topico=str(topico or "").strip()[:160],
    )


def obter_configuracao(aluno):
    return ConfiguracaoTutor.objects.get_or_create(usuario=aluno)[0]


def responder_mensagem(*, conversa, conteudo, gateway=None):
    conteudo = str(conteudo or "").strip()
    if not conteudo:
        raise ValueError("A mensagem nao pode ser vazia.")
    gateway = gateway or GatewayIA.from_settings()
    with transaction.atomic():
        mensagem_aluno = Mensagem.objects.create(
            conversa=conversa,
            papel=PapelMensagem.ALUNO,
            conteudo=conteudo,
        )
        contexto = recuperar_contexto(
            conversa.aluno,
            disciplina=conversa.disciplina,
            topico=conversa.topico,
            conversa=conversa,
        )
        prompt = _montar_prompt(
            conversa,
            contexto["texto"],
            conteudo,
            obter_configuracao(conversa.aluno),
        )
        chamada, texto = gateway.chamar(
            instituicao=conversa.aluno.instituicao,
            usuario=conversa.aluno,
            classe_tarefa="TUTORIA",
            prompt=prompt,
            devolver_texto=True,
        )
        mensagem_tutor = Mensagem.objects.create(
            conversa=conversa,
            papel=PapelMensagem.TUTOR,
            conteudo=texto,
            chamada_ia=chamada,
        )
    return mensagem_aluno, mensagem_tutor


def _montar_prompt(conversa, contexto, conteudo, configuracao):
    partes = [
        "Voce e o tutor de estudos do aluno.",
        f"Materia: {conversa.disciplina or 'nao informada'}.",
        f"Topico: {conversa.topico or 'nao informado'}.",
        f"Estilo: {configuracao.estilo}; dificuldade: {configuracao.dificuldade}; "
        f"respostas: {configuracao.tamanho_resposta}; exame: {configuracao.foco_exame}.",
    ]
    if contexto:
        partes.append(f"Contexto de estudo anterior:\n{contexto}")
    partes.append(f"Pergunta atual do aluno:\n{conteudo}")
    return "\n\n".join(partes)
