from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.utils import timezone

from ia.gateway import GatewayIA

from .models import QuestaoSimulado, Simulado, StatusSimulado
from .questoes_ia import interpretar_questoes, montar_prompt


def gerar_simulado(
    *,
    aluno,
    disciplina,
    estilo="ENEM",
    quantidade,
    foco_dificuldades=True,
    correcao_comentada=True,
    gateway=None,
):
    gateway = gateway or GatewayIA.from_settings()
    chamada, texto = gateway.chamar(
        instituicao=aluno.instituicao,
        usuario=aluno,
        classe_tarefa="GERACAO",
        prompt=montar_prompt(
            disciplina=disciplina,
            estilo=estilo,
            quantidade=quantidade,
            foco_dificuldades=foco_dificuldades,
            correcao_comentada=correcao_comentada,
        ),
        devolver_texto=True,
    )
    # Fora da transacao de proposito: se o modelo nao honrar o contrato, nada
    # e criado e o erro sobe. O consumo ja debitado permanece porque a chamada
    # realmente aconteceu e realmente custou - inventar questao para "aproveitar"
    # o debito e o que este servico fazia antes.
    questoes = interpretar_questoes(texto, quantidade=quantidade)
    with transaction.atomic():
        simulado = Simulado.objects.create(
            instituicao=aluno.instituicao,
            aluno=aluno,
            disciplina=disciplina,
            estilo=estilo,
            quantidade=quantidade,
            foco_dificuldades=foco_dificuldades,
            correcao_comentada=correcao_comentada,
            chamada_ia=chamada,
        )
        QuestaoSimulado.objects.bulk_create(
            QuestaoSimulado(
                simulado=simulado,
                ordem=ordem,
                enunciado=questao.enunciado,
                alternativas=questao.alternativas,
                gabarito=questao.gabarito,
            )
            for ordem, questao in enumerate(questoes, start=1)
        )
    return simulado


def responder_questao(*, simulado, questao, alternativa):
    if simulado.status != StatusSimulado.EM_ANDAMENTO:
        raise ValueError("O simulado ja foi finalizado.")
    alternativa = str(alternativa or "").strip().upper()
    if alternativa not in {"A", "B", "C", "D"}:
        raise ValueError("Alternativa invalida.")
    questao.resposta = alternativa
    questao.save(update_fields=["resposta"])
    return questao


def finalizar_simulado(*, simulado):
    if simulado.status == StatusSimulado.CONCLUIDO:
        return simulado
    questoes = list(simulado.questoes.all())
    acertos = sum(questao.resposta == questao.gabarito for questao in questoes)
    percentual = (
        (Decimal(acertos) * Decimal("100") / Decimal(len(questoes))).quantize(
            Decimal("0.0001"), rounding=ROUND_HALF_UP
        )
        if questoes
        else Decimal("0")
    )
    with transaction.atomic():
        simulado.status = StatusSimulado.CONCLUIDO
        simulado.resultado_percentual = percentual
        simulado.concluido_em = timezone.now()
        simulado.save(update_fields=["status", "resultado_percentual", "concluido_em"])
    return simulado
