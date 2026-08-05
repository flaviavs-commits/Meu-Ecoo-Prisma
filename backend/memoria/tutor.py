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
    # O gateway roda FORA de transacao. Antes, todo este bloco era um
    # `atomic()`: alem de segurar a transacao durante a chamada de rede, uma
    # falha revertia junto o `ChamadaIA` de erro que o proprio gateway acabara
    # de gravar - a auditoria de falha existia pelo simulado e sumia pelo tutor.
    chamada, texto = gateway.chamar(
        instituicao=conversa.aluno.instituicao,
        usuario=conversa.aluno,
        classe_tarefa="TUTORIA",
        prompt=prompt,
        devolver_texto=True,
    )
    # As duas mensagens nascem juntas ou nao nascem: pergunta sem resposta
    # deixaria a conversa em estado que a tela nao sabe representar.
    with transaction.atomic():
        mensagem_aluno = Mensagem.objects.create(
            conversa=conversa,
            papel=PapelMensagem.ALUNO,
            conteudo=conteudo,
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
