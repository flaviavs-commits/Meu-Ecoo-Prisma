"""O que cada card do HUD faz quando clicado.

Mixin da classe `Hud`. Cada `acao_*` corresponde a um card da grade.
"""

from __future__ import annotations

import subprocess
import sys
import threading
import webbrowser
from pathlib import Path

from .ambiente import dependencias_instaladas, npm, porta_em_uso, portas_em_escuta
from .caminhos import FRONTEND, RAIZ, SINCRONIZAR_APP
from .processos import SAIDA_SUBPROCESSO, encerrar_arvore, encerrar_pid
from .tokens import ICONES
from .widgets import Modal, PainelPortas


class AcoesMixin:
    """Acoes dos cards e o ciclo de vida do servidor."""

    # -- apoio ---------------------------------------------------------

    def _rodar_comando(
        self, argumentos: list[str], titulo: str, sucesso: str, falha: str, cwd: Path
    ) -> None:
        """Roda um comando em thread, transmitindo a saida para o console."""
        if self.ocupado:
            self._escrever("Já há uma ação em andamento.", "suave")
            return

        self._travar_cards(True)
        self._escrever(f"$ {titulo}", "suave")

        def trabalho() -> None:
            try:
                processo = subprocess.Popen(argumentos, cwd=cwd, **SAIDA_SUBPROCESSO)
            except OSError as exc:
                self.fila.put(("erro", f"Falha ao executar: {exc}"))
                self.fila.put(("toast_erro", falha))
                self.fila.put(("fim", ""))
                return

            assert processo.stdout is not None
            for linha in processo.stdout:
                self.fila.put(("", linha.rstrip()))

            if processo.wait() == 0:
                self.fila.put(("ok", sucesso))
                self.fila.put(("toast_ok", sucesso))
            else:
                self.fila.put(("erro", falha))
                self.fila.put(("toast_erro", falha))
            self.fila.put(("fim", ""))

        threading.Thread(target=trabalho, daemon=True).start()

    def _npm_ou_avisa(self) -> str | None:
        executavel = npm()
        if executavel is None:
            self._escrever("npm não encontrado no PATH.", "erro")
            self._escrever("Instale o Node.js 20+ em https://nodejs.org", "suave")
            self._toast_mostrar("npm não encontrado", False)
        return executavel

    def _deps_ou_avisa(self) -> bool:
        if dependencias_instaladas():
            return True
        self._escrever("Dependências ausentes - use 'Instalar dependências'.", "erro")
        self._toast_mostrar("Instale as dependências antes", False)
        return False

    # -- servidor ------------------------------------------------------

    def acao_servidor(self) -> None:
        """Card principal: sobe ou para o frontend em localhost.

        So cuida do frontend, de proposito. O backend e outra
        responsabilidade, com o proprio card ('Rodar backend') - assim
        uma falha na API nunca impede a landing page de subir.
        """
        rodando = self.servidor is not None and self.servidor.poll() is None
        if self.ocupado and not rodando:
            self._escrever("O frontend ainda esta sendo preparado.", "suave")
            return
        if rodando:
            self._parar_servidor()
        else:
            self._subir_servidor()

    def _subir_servidor(self) -> bool:
        executavel = self._npm_ou_avisa()
        if executavel is None or not self._deps_ou_avisa():
            return False

        if porta_em_uso(self.porta):
            self._escrever(f"A porta {self.porta} já está em uso.", "erro")
            self._escrever("Use 'Porta' para escolher outra, ou encerre o outro processo.", "suave")
            self._toast_mostrar(f"Porta {self.porta} ocupada", False)
            return False

        self._escrever(f"$ npm run dev -- --port {self.porta}", "suave")

        try:
            self.servidor = subprocess.Popen(
                [executavel, "run", "dev", "--", "--port", str(self.porta)],
                cwd=FRONTEND,
                **SAIDA_SUBPROCESSO,
            )
        except OSError as exc:
            self._escrever(f"Falha ao subir o servidor: {exc}", "erro")
            self._toast_mostrar("Não foi possível subir", False)
            return False

        processo = self.servidor
        self._card_servidor_para()
        self._toast_mostrar("Servidor iniciado")

        def acompanhar() -> None:
            if processo.stdout is None:
                return
            for linha in processo.stdout:
                self.fila.put(("", linha.rstrip()))
            self.fila.put(("suave", "O servidor encerrou."))

        threading.Thread(target=acompanhar, daemon=True).start()
        return True

    def _parar_servidor(self) -> None:
        processo = self.servidor
        if processo is None or processo.poll() is not None:
            self.servidor = None
            return

        self.servidor = None
        self._escrever("Encerrando o servidor...", "suave")
        self._card_servidor_roda()

        # O wait pode levar segundos; na thread da interface isso
        # congelaria a janela justamente enquanto ela diz que esta
        # encerrando.
        def encerrar() -> None:
            encerrar_arvore(processo)
            self.fila.put(("ok", "Servidor encerrado."))
            self.fila.put(("toast_ok", "Servidor encerrado"))

        threading.Thread(target=encerrar, daemon=True).start()

    # -- demais cards --------------------------------------------------

    def acao_abrir(self) -> None:
        endereco = f"http://localhost:{self.porta}/"
        if not porta_em_uso(self.porta):
            self._escrever(f"Nada respondendo em {endereco}", "erro")
            self._toast_mostrar("Suba o servidor antes", False)
            return
        webbrowser.open(endereco)
        self._escrever(f"Abrindo {endereco}", "suave")

    def acao_instalar(self) -> None:
        executavel = self._npm_ou_avisa()
        if executavel is None:
            return
        self._rodar_comando(
            [executavel, "install"], "npm install",
            "Dependências instaladas.", "A instalação falhou.", FRONTEND,
        )

    def acao_build(self) -> None:
        executavel = self._npm_ou_avisa()
        if executavel is None or not self._deps_ou_avisa():
            return
        self._rodar_comando(
            [executavel, "run", "build"], "npm run build",
            "Build concluído em frontend/dist.", "O build falhou.", FRONTEND,
        )

    def acao_validar(self) -> None:
        executavel = self._npm_ou_avisa()
        if executavel is None or not self._deps_ou_avisa():
            return
        self._rodar_comando(
            [executavel, "run", "lint"], "npm run lint",
            "Lint aprovado. Rode 'Build' para completar.", "O lint reprovou.", FRONTEND,
        )

    def acao_sincronizar(self) -> None:
        if not SINCRONIZAR_APP.is_file():
            self._escrever(f"Script não encontrado: {SINCRONIZAR_APP}", "erro")
            self._toast_mostrar("Script ausente", False)
            return
        self._rodar_comando(
            [sys.executable, str(SINCRONIZAR_APP)], "python scripts/sincronizar-app.py",
            "Telas sincronizadas.", "A sincronização falhou.", RAIZ,
        )

    def acao_limpar(self) -> None:
        self.console.config(state="normal")
        self.console.delete("1.0", "end")
        self.console.config(state="disabled")
        self._escrever("Console limpo.", "suave")

    def acao_configurar(self) -> None:
        modal = Modal(
            self.raiz,
            self.fontes,
            "Porta do servidor",
            "Onde o Vite vai servir a landing.",
            confirmar="Salvar",
            valor_inicial=str(self.porta),
            dica="Entre 1024 e 65535. Enter confirma, Esc cancela.",
        )
        escolha = modal.esperar()
        if escolha is None:
            return

        texto = escolha.strip()
        if not texto.isdigit() or not 1024 <= int(texto) <= 65535:
            self._escrever(f"Porta inválida: {texto or '(vazio)'}", "erro")
            self._toast_mostrar("Porta inválida", False)
            return

        self.porta = int(texto)
        self.cards["porta"].definir_conteudo(
            ICONES["porta"], "Porta frontend", f"Atual: {self.porta}"
        )
        self._escrever(f"Porta definida para {self.porta}.", "ok")
        self._toast_mostrar(f"Porta {self.porta}")

    def acao_fechar_porta(self) -> None:
        """Abre o painel com todas as portas em uso, para encerrar qualquer uma."""
        if self.ocupado:
            self._escrever("Já há uma ação em andamento.", "suave")
            return

        self._escrever("Consultando portas em uso...", "suave")
        self.raiz.update_idletasks()
        portas = portas_em_escuta()

        meu_pid = self.servidor.pid if self.servidor and self.servidor.poll() is None else None
        if meu_pid is not None:
            # O servidor deste HUD tem card proprio para parar; misturar
            # os dois caminhos de encerramento so confundiria qual botao
            # usar.
            portas = [item for item in portas if item.pid != meu_pid]

        PainelPortas(self.raiz, self.fontes, portas, self._encerrar_porta)

    def _encerrar_porta(self, item) -> None:
        self._escrever(f"Encerrando {item.processo} (PID {item.pid}) na porta {item.porta}...", "suave")

        def trabalho() -> None:
            if not encerrar_pid(item.pid):
                self.fila.put(("erro", f"Falha ao encerrar PID {item.pid}."))
                self.fila.put(("toast_erro", "Falha ao encerrar processo"))
            else:
                self.fila.put(("ok", f"Porta {item.porta} liberada."))
                self.fila.put(("toast_ok", f"Porta {item.porta} liberada"))

        threading.Thread(target=trabalho, daemon=True).start()

    def ao_fechar(self) -> None:
        """Nao deixa os servidores locais orfaos quando a janela fecha."""
        processos = [
            processo
            for processo in (self.servidor, self.backend)
            if processo and processo.poll() is None
        ]
        if processos:
            modal = Modal(
                self.raiz,
                self.fontes,
                "Encerrar o servidor?",
                "Há servidores locais rodando. Fechar o HUD encerra os "
                "processos junto.",
                confirmar="Encerrar",
                cancelar="Manter aberto",
            )
            if modal.esperar() is None:
                # "Manter aberto" cancela o fechamento inteiro: fechar a
                # janela assim mesmo deixaria um servidor local segurando a
                # porta, que e justamente o que o aviso quer evitar.
                return

            # Aqui o encerramento e sincrono de proposito: a thread do
            # `_parar_servidor` e daemon e morreria junto com o processo,
            # deixando um servidor local orfao.
            self.servidor = None
            self.backend = None
            for processo in processos:
                encerrar_arvore(processo)
        self.raiz.destroy()
