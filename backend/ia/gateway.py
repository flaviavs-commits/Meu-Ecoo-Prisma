import time

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from creditos.consumo import autorizar_consumo, registrar_consumo, trava_saldo
from creditos.excecoes import SaldoInsuficienteError

from .conversao import custo_para_creditos
from .excecoes import ProvedorIAError
from .models import ChamadaIA, StatusChamada
from .provedores.falso import ProvedorFalso
from .provedores.openrouter import ProvedorOpenRouter
from .roteamento import modelo_para_classe


class GatewayIA:
    """Unica porta de entrada para chamadas de IA e seu debito contabil."""

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
    ):
        if chamada and chamada.status == StatusChamada.SUCESSO:
            return chamada
        chamada = chamada or ChamadaIA.objects.create(
            instituicao=instituicao,
            usuario=usuario,
            classe_tarefa=classe_tarefa,
        )
        modelo = modelo_para_classe(classe_tarefa)
        try:
            with trava_saldo(usuario):
                autorizar_consumo(usuario)
                resultado = self._gerar_com_retry(prompt, modelo)
                creditos = custo_para_creditos(
                    resultado.custo_bruto,
                    custo_por_credito=settings.IA_CUSTO_POR_CREDITO,
                    margem=settings.IA_MARGEM_CREDITOS,
                )
                with transaction.atomic():
                    registrar_consumo(
                        instituicao=instituicao,
                        usuario=usuario,
                        quantidade=creditos,
                        motivo=f"Uso de IA: {classe_tarefa}",
                        referencia=chamada,
                        criado_por=usuario,
                    )
                    chamada.modelo = resultado.modelo
                    chamada.tokens_entrada = resultado.tokens_entrada
                    chamada.tokens_saida = resultado.tokens_saida
                    chamada.custo_bruto = resultado.custo_bruto
                    chamada.creditos_debitados = creditos
                    chamada.status = StatusChamada.SUCESSO
                    chamada.concluida_em = timezone.now()
                    chamada.save()
        except SaldoInsuficienteError as erro:
            self._marcar_erro(chamada, erro.codigo)
            raise
        except ProvedorIAError as erro:
            self._marcar_erro(chamada, erro.codigo)
            raise
        except TimeoutError:
            self._marcar_erro(chamada, "timeout_provedor")
            raise ProvedorIAError("Tempo limite do provedor excedido.", codigo="timeout_provedor")
        return chamada

    def _gerar_com_retry(self, prompt, modelo):
        for tentativa in range(3):
            try:
                return self.provedor.gerar(prompt, modelo, timeout=self.timeout)
            except ProvedorIAError as erro:
                if not erro.transitorio or tentativa == 2:
                    raise
                self._dormir(0.05 * (2**tentativa))

    @staticmethod
    def _marcar_erro(chamada, codigo):
        chamada.status = StatusChamada.ERRO
        chamada.erro_codigo = codigo
        chamada.concluida_em = timezone.now()
        chamada.save(update_fields=["status", "erro_codigo", "concluida_em"])
