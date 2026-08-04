"""Leitura periodica do ambiente e pintura do card de status.

Mixin da classe `Hud`. A medicao roda em thread; a pintura, nunca -
o Tkinter so aceita chamada da thread principal.
"""

from __future__ import annotations

import threading

from .ambiente import app_sincronizada, dependencias_instaladas, npm, porta_em_uso
from .tokens import (
    ALERTA,
    ALERTA_FUNDO,
    ERRO,
    ERRO_FUNDO,
    FUNDO,
    ICONES,
    INFO,
    INFO_FUNDO,
    SUCESSO,
    SUCESSO_FUNDO,
    TEXTO_TENUE,
)


class StatusMixin:
    """Mede o ambiente e mantem o card de status em dia."""

    def _agendar_status(self) -> None:
        """Mede o estado do ambiente fora da thread da interface.

        `porta_em_uso` bloqueia ate 0,25 s por familia de endereco - com a
        porta livre, as duas gastam o timeout. Rodar isso direto no laco
        do Tkinter congelaria a janela a cada ciclo.

        A thread NAO toca em widget nem chama `after`: o Tkinter so aceita
        chamada da thread principal ("main thread is not in main loop").
        O resultado volta pela mesma fila que a saida dos comandos usa.
        """

        def medir() -> None:
            frontend = "1" if porta_em_uso(self.porta) else ""
            backend = "1" if porta_em_uso(self.porta_backend) else ""
            self.fila.put(("status", f"{frontend}:{backend}"))

        threading.Thread(target=medir, daemon=True).start()
        self.raiz.after(3000, self._agendar_status)

    def _pintar_status(self, estado: str) -> None:
        """Repinta o card de status. So roda na thread da interface."""
        frontend_ocupado, backend_ocupado = estado.split(":")
        frontend_ocupado = frontend_ocupado == "1"
        backend_ocupado = backend_ocupado == "1"
        meu_frontend = self.servidor is not None and self.servidor.poll() is None
        meu_backend = self.backend is not None and self.backend.poll() is None
        # O card principal cuida so do frontend: e o que ele liga e
        # desliga, entao e o unico que decide se vira 'Parar aplicacao'.
        self.rodando = meu_frontend

        def estado_porta(ocupada: bool, proprio: bool):
            if ocupada and proprio:
                return ("Rodando", SUCESSO, SUCESSO_FUNDO)
            if ocupada:
                return ("Externo", ALERTA, ALERTA_FUNDO)
            return ("Parado", TEXTO_TENUE, FUNDO)

        deps = dependencias_instaladas()
        telas = app_sincronizada()
        tem_npm = npm() is not None

        self.linhas["Frontend"].atualizar(*estado_porta(frontend_ocupado, meu_frontend))
        self.linhas["Backend"].atualizar(*estado_porta(backend_ocupado, meu_backend))
        self.linhas["Dependências"].atualizar(
            *(("Instaladas", SUCESSO, SUCESSO_FUNDO) if deps else ("Ausentes", ALERTA, ALERTA_FUNDO))
        )
        self.linhas["Telas da aplicação"].atualizar(
            *(("Sincronizadas", SUCESSO, SUCESSO_FUNDO) if telas else ("Ausentes", ALERTA, ALERTA_FUNDO))
        )
        self.linhas["npm"].atualizar(
            *(("Encontrado", SUCESSO, SUCESSO_FUNDO) if tem_npm else ("Ausente", ERRO, ERRO_FUNDO))
        )
        self.linhas["Porta frontend"].atualizar(str(self.porta), INFO, INFO_FUNDO)
        self.linhas["Porta backend"].atualizar(str(self.porta_backend), INFO, INFO_FUNDO)

        # O card principal alterna entre subir e parar o frontend.
        if meu_frontend:
            self._card_servidor_para()
        elif not self.ocupado:
            self._card_servidor_roda()

        # "Abrir navegador" so faz sentido com algo respondendo.
        if not self.ocupado:
            self.cards["abrir"].definir_estado(frontend_ocupado)
            self.cards["backend"].definir_estado(True)

    def _card_servidor_para(self) -> None:
        """Poe o card principal no modo 'parar'."""
        self.cards["servidor"].definir_conteudo(
            ICONES["parar"], "Parar aplicação", "Finaliza o frontend em localhost"
        )

    def _card_servidor_roda(self) -> None:
        """Poe o card principal no modo 'rodar'."""
        self.cards["servidor"].definir_conteudo(
            ICONES["rodar"], "Rodar aplicação", "Inicia o frontend em localhost"
        )

    def _travar_cards(self, travar: bool) -> None:
        """Desabilita as acoes durante um comando.

        'servidor' fica de fora: parar o servidor e justamente o que a
        pessoa precisa quando algo esta em andamento.
        """
        self.ocupado = travar
        for chave, card in self.cards.items():
            if chave in ("servidor", "backend"):
                continue
            if chave == "abrir" and not travar:
                # Quem manda no estado deste e o _pintar_status.
                continue
            card.definir_estado(not travar)
