from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from creditos.models import Lancamento, TipoLancamento
from ia.gateway import GatewayIA
from ia.provedores.falso import ProvedorFalso
from memoria.consolidacao import compactar_memorias, consolidar_conversa
from memoria.contexto import recuperar_contexto
from memoria.models import (
    Conversa,
    MemoriaConsolidada,
    MemoriaImutavelError,
    Mensagem,
    PapelMensagem,
)

pytestmark = pytest.mark.django_db


def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


def creditar(aluno, quantidade="20"):
    return Lancamento.objects.create(
        instituicao=aluno.instituicao,
        usuario=aluno,
        tipo=TipoLancamento.CREDITO,
        quantidade=Decimal(quantidade),
        motivo="carga de memoria",
    )


def conversa_com_mensagens(aluno):
    conversa = Conversa.objects.create(aluno=aluno, titulo="Fracoes")
    Mensagem.objects.create(
        conversa=conversa,
        papel=PapelMensagem.ALUNO,
        conteudo="Como somo fracoes?",
    )
    Mensagem.objects.create(
        conversa=conversa,
        papel=PapelMensagem.TUTOR,
        conteudo="Use um denominador comum.",
    )
    return conversa


def test_conversa_guarda_mensagens_na_ordem(aluno):
    conversa = conversa_com_mensagens(aluno)

    assert list(conversa.mensagens.values_list("papel", flat=True)) == [
        PapelMensagem.ALUNO,
        PapelMensagem.TUTOR,
    ]


def test_consolidacao_cria_memoria_sem_alterar_bruto(aluno):
    creditar(aluno)
    conversa = conversa_com_mensagens(aluno)
    gateway = GatewayIA(provedor=ProvedorFalso())

    memoria = consolidar_conversa(
        conversa, gateway=gateway, disciplina="matematica", topico="fracoes"
    )

    assert memoria.resumo == "Resposta deterministica do provedor falso."
    assert conversa.mensagens.count() == 2
    assert Mensagem.objects.filter(conversa=conversa).exists()


def test_consolidacao_debita_credito_via_gateway(aluno):
    creditar(aluno)
    conversa = conversa_com_mensagens(aluno)

    consolidar_conversa(conversa, gateway=GatewayIA(provedor=ProvedorFalso()))

    assert Lancamento.objects.filter(
        usuario=aluno, tipo=TipoLancamento.DEBITO
    ).count() == 1


def test_recuperacao_filtra_e_respeita_teto_de_tokens(aluno):
    conversa = conversa_com_mensagens(aluno)
    MemoriaConsolidada.objects.create(
        aluno=aluno,
        disciplina="matematica",
        topico="fracoes",
        resumo="Memoria relevante",
    )
    MemoriaConsolidada.objects.create(
        aluno=aluno,
        disciplina="historia",
        topico="imperio",
        resumo="Memoria irrelevante",
    )

    contexto = recuperar_contexto(
        aluno,
        disciplina="matematica",
        topico="fracoes",
        conversa=conversa,
        limite_tokens=5,
    )

    assert "Memoria relevante" in contexto["memorias"]
    assert "Memoria irrelevante" not in contexto["memorias"]
    assert contexto["tokens_estimados"] <= 5


def test_compactacao_cria_nova_memoria_sem_apagar_originais(aluno):
    creditar(aluno)
    primeira = MemoriaConsolidada.objects.create(
        aluno=aluno, disciplina="matematica", topico="fracoes", resumo="Parte um"
    )
    segunda = MemoriaConsolidada.objects.create(
        aluno=aluno, disciplina="matematica", topico="fracoes", resumo="Parte dois"
    )

    nova = compactar_memorias(
        aluno,
        gateway=GatewayIA(provedor=ProvedorFalso()),
        disciplina="matematica",
        topico="fracoes",
    )

    assert nova.pk not in {primeira.pk, segunda.pk}
    assert MemoriaConsolidada.objects.filter(pk=primeira.pk).exists()
    assert MemoriaConsolidada.objects.filter(pk=segunda.pk).exists()


def test_professor_nao_le_conversa_crua(aluno, professor):
    conversa = conversa_com_mensagens(aluno)

    resposta = cliente(professor).get(f"/api/v1/memoria/conversas/{conversa.id}/")

    assert resposta.status_code == 403


def test_diretor_nao_le_conversa_crua(aluno, diretor):
    conversa = conversa_com_mensagens(aluno)

    resposta = cliente(diretor).get(f"/api/v1/memoria/conversas/{conversa.id}/")

    assert resposta.status_code == 403


def test_aluno_de_outra_instituicao_recebe_404(aluno, outro_aluno):
    conversa = conversa_com_mensagens(aluno)

    resposta = cliente(outro_aluno).get(f"/api/v1/memoria/conversas/{conversa.id}/")

    assert resposta.status_code == 404


def test_conteudo_de_mensagem_nao_aparece_em_log(aluno, caplog):
    conversa = Conversa.objects.create(aluno=aluno, titulo="Privado")
    conteudo = "segredo de aprendizagem"
    Mensagem.objects.create(
        conversa=conversa, papel=PapelMensagem.ALUNO, conteudo=conteudo
    )

    assert conteudo not in caplog.text


def test_memoria_consolidada_recusa_update(aluno):
    memoria = MemoriaConsolidada.objects.create(
        aluno=aluno, disciplina="matematica", resumo="original"
    )
    memoria.resumo = "alterado"

    with pytest.raises(MemoriaImutavelError):
        memoria.save()
