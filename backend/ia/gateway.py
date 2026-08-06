import time
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from custos.rateio import custo_da_chamada
from limites.excecoes import LimiteDeUsoExcedidoError
from limites.servico import autorizar_uso, registrar_uso, trava_cota

from .conversao import custo_para_percentual
from .excecoes import ChamadaConcorrenteError, ProvedorIAError
from .models import ChamadaIA, StatusChamada
from .provedores.falso import ProvedorFalso
from .provedores.openrouter import ProvedorOpenRouter
from .roteamento import modelo_para_classe


class GatewayIA:
    """Unica porta de entrada para chamadas de IA e seu debito contabil."""

    TENTATIVAS = 3

    def __init__(self, provedor, *, timeout=None, dormir=time.sleep):
        self.provedor = provedor
        self.timeout = timeout or settings.IA_TIMEOUT_SEGUNDOS
        self._dormir = dormir

    @classmethod
    def from_settings(cls):
        provedores = {
            "falso": ProvedorFalso,
            "openrouter": ProvedorOpenRouter,
        }
        try:
            provedor = provedores[settings.IA_PROVEDOR]()
        except KeyError as erro:
            raise ValueError("IA_PROVEDOR precisa ser falso ou openrouter.") from erro
        return cls(provedor)

    @classmethod
    def openrouter(cls):
        return cls(ProvedorOpenRouter())

    def chamar(
        self,
        *,
        instituicao,
        usuario,
        classe_tarefa,
        prompt,
        chamada=None,
        devolver_texto=False,
    ):
        if chamada and chamada.status == StatusChamada.SUCESSO:
            return (chamada, "") if devolver_texto else chamada
        chamada = chamada or ChamadaIA.objects.create(
            instituicao=instituicao,
            usuario=usuario,
            classe_tarefa=classe_tarefa,
        )
        modelo = modelo_para_classe(classe_tarefa)
        try:
            # 1. Portao. Transacao curta, so para decidir se pode comecar.
            #    A chamada externa fica FORA dela: segurar a trava da cota
            #    durante ate tres tentativas de HTTP deixava uma transacao
            #    aberta por dezenas de segundos por request.
            with trava_cota(usuario):
                autorizar_uso(usuario)
                self._recusar_chamada_concorrente(usuario, chamada)

            # 2. Provedor, sem transacao aberta.
            resultado = self._gerar_com_retry(prompt, modelo)
            fornecedor = getattr(resultado, "fornecedor", "desconhecido")
            # O custo passa pelo contrato do fornecedor antes de virar
            # percentual: e o que coloca uma chamada cobrada por token e a fatia
            # de uma assinatura na mesma unidade. Sem isto, chamada atendida por
            # assinatura chega com custo zero e nao consome nada da conta.
            custo = custo_da_chamada(
                fornecedor=fornecedor,
                modelo=resultado.modelo,
                tokens_entrada=resultado.tokens_entrada,
                tokens_saida=resultado.tokens_saida,
                custo_reportado=resultado.custo_bruto,
            )
            percentual = custo_para_percentual(
                custo,
                custo_dolar_por_percentual=settings.IA_CUSTO_DOLAR_POR_PERCENTUAL,
                margem=settings.IA_MARGEM_USO,
            )

            # 3. Debito. O provedor ja cobrou, entao o consumo e um fato e e
            #    sempre registrado - mesmo que estoure o restante do plano.
            #    Recusar aqui deixava o custo existindo no fornecedor e nao
            #    existindo na nossa contabilidade. O estouro so pode ser de uma
            #    chamada, porque o portao acima ja barra a proxima.
            with transaction.atomic():
                registrar_uso(
                    usuario=usuario,
                    percentual=percentual,
                    fornecedor=fornecedor,
                    modelo=resultado.modelo,
                    classe_tarefa=classe_tarefa,
                    referencia=chamada,
                    custo_bruto=custo,
                )
                chamada.modelo = resultado.modelo
                chamada.tokens_entrada = resultado.tokens_entrada
                chamada.tokens_saida = resultado.tokens_saida
                chamada.custo_bruto = custo
                chamada.fornecedor = fornecedor
                chamada.percentual_debitado = percentual
                chamada.status = StatusChamada.SUCESSO
                chamada.concluida_em = timezone.now()
                chamada.save()
        except (LimiteDeUsoExcedidoError, ChamadaConcorrenteError) as erro:
            self._marcar_erro(chamada, erro.codigo)
            raise
        except ProvedorIAError as erro:
            self._marcar_erro(chamada, erro.codigo)
            raise
        except TimeoutError:
            self._marcar_erro(chamada, "timeout_provedor")
            raise ProvedorIAError("Tempo limite do provedor excedido.", codigo="timeout_provedor")
        return (chamada, resultado.texto) if devolver_texto else chamada

    def _recusar_chamada_concorrente(self, usuario, chamada):
        """Uma chamada por conta de cada vez, decidida sob a trava da cota.

        Compara por `pk` para que duas requisicoes simultaneas nao se recusem
        mutuamente: a mais antiga segue, a mais nova espera. Chamada pendente
        mais velha que a janela de abandono e considerada orfa (processo morto
        no meio), senao um crash travaria a conta para sempre.
        """
        limite_abandono = timezone.now() - timedelta(
            seconds=self.timeout * self.TENTATIVAS * 2
        )
        em_curso = (
            ChamadaIA.objects.filter(
                usuario=usuario,
                status=StatusChamada.PENDENTE,
                criada_em__gte=limite_abandono,
                pk__lt=chamada.pk,
            )
            .exclude(pk=chamada.pk)
            .exists()
        )
        if em_curso:
            raise ChamadaConcorrenteError(
                "Ja existe uma chamada de IA em andamento para esta conta."
            )

    def _gerar_com_retry(self, prompt, modelo):
        ultima = self.TENTATIVAS - 1
        for tentativa in range(self.TENTATIVAS):
            try:
                return self.provedor.gerar(prompt, modelo, timeout=self.timeout)
            except ProvedorIAError as erro:
                if not erro.transitorio or tentativa == ultima:
                    raise
                self._dormir(0.05 * (2**tentativa))

    @staticmethod
    def _marcar_erro(chamada, codigo):
        chamada.status = StatusChamada.ERRO
        chamada.erro_codigo = codigo
        chamada.concluida_em = timezone.now()
        chamada.save(update_fields=["status", "erro_codigo", "concluida_em"])
