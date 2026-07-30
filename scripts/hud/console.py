"""Terminal embutido do HUD: linha de comando, historico e execucao.

Mixin da classe `Hud`. Usa da janela: `entrada`, `console`,
`rotulo_pasta`, `fila`, `ocupado` e `_escrever`.
"""

from __future__ import annotations

import subprocess
import threading

from .caminhos import FRONTEND, RAIZ
from .processos import SAIDA_BYTES, decodificar, encerrar_arvore


class ConsoleMixin:
    """Comportamento da linha de comando do console."""

    def _enviar_comando(self, _evento=None) -> str:
        """Executa o que foi digitado, como um terminal faria."""
        texto = self.entrada.get().strip()
        self.entrada.delete(0, "end")
        if not texto:
            return "break"

        self.historico.append(texto)
        self.indice_historico = len(self.historico)
        self._escrever(f"❯ {texto}", "comando")

        if self._comando_interno(texto):
            return "break"

        if self.ocupado:
            self._escrever("Já há uma ação em andamento. Ctrl+C interrompe.", "suave")
            return "break"

        self._rodar_shell(texto)
        return "break"

    def _comando_interno(self, texto: str) -> bool:
        """Atalhos que o proprio HUD resolve, sem abrir subprocesso."""
        comando = texto.lower()
        if comando in ("clear", "cls", "limpar"):
            self.acao_limpar()
            return True
        if comando in ("exit", "quit", "sair"):
            self.ao_fechar()
            return True
        if comando in ("pwd", "cd"):
            self._escrever(str(self.pasta_console), "suave")
            return True
        if comando.startswith("cd "):
            # `cd` precisa ser interno: num subprocesso ele mudaria a
            # pasta do processo filho e morreria junto com ele.
            self._mudar_pasta(texto[3:].strip().strip('"'))
            return True
        if comando in ("help", "ajuda", "?"):
            self._escrever("Digite qualquer comando de terminal. Internos:", "suave")
            self._escrever("  cd <pasta>   muda de pasta      pwd   mostra a pasta", "suave")
            self._escrever("  clear        limpa o console    exit  fecha o HUD", "suave")
            self._escrever("  Ctrl+C       interrompe o comando em andamento", "suave")
            self._escrever("  ↑ ↓          percorre o histórico", "suave")
            return True
        return False

    def _mudar_pasta(self, destino: str) -> None:
        """Muda a pasta corrente do console."""
        alvo = (self.pasta_console / destino).resolve() if destino else RAIZ
        if not alvo.is_dir():
            self._escrever(f"Pasta não encontrada: {alvo}", "erro")
            return
        self.pasta_console = alvo
        self._atualizar_prompt()
        self._escrever(str(alvo), "suave")

    def _atualizar_prompt(self) -> None:
        """Mostra no rotulo do console onde os comandos vao rodar."""
        try:
            relativo = self.pasta_console.relative_to(RAIZ)
            nome = f"~/{relativo.as_posix()}" if relativo.parts else "~"
        except ValueError:
            nome = str(self.pasta_console)
        self.rotulo_pasta.config(text=nome)

    def _rodar_shell(self, comando: str) -> None:
        """Roda um comando arbitrario na pasta corrente do console.

        Vai pelo shell para que `npm run dev`, pipes e variaveis se
        comportem como a pessoa espera do terminal.
        """
        self._travar_cards(True)

        pasta = self.pasta_console

        def trabalho() -> None:
            try:
                processo = subprocess.Popen(
                    comando, cwd=pasta, shell=True, **SAIDA_BYTES
                )
            except OSError as exc:
                self.fila.put(("erro", f"Falha ao executar: {exc}"))
                self.fila.put(("fim", ""))
                return

            self.processo_shell = processo
            assert processo.stdout is not None
            for bruto in processo.stdout:
                self.fila.put(("", decodificar(bruto).rstrip()))

            codigo = processo.wait()
            self.processo_shell = None
            if codigo != 0:
                # No Windows o codigo vem sem sinal: -4058 chega como
                # 4294963238. Converter deixa a mensagem util.
                if codigo > 2**31:
                    codigo -= 2**32
                self.fila.put(("erro", f"[saiu com código {codigo}]"))
            self.fila.put(("fim", ""))

        threading.Thread(target=trabalho, daemon=True).start()

    def _interromper(self, _evento=None) -> str:
        """Ctrl+C: encerra o comando em andamento, como num terminal."""
        processo = self.processo_shell
        if processo is not None and processo.poll() is None:
            self._escrever("^C", "suave")
            threading.Thread(
                target=encerrar_arvore, args=(processo,), daemon=True
            ).start()
        return "break"

    def _historico_anterior(self, _evento=None) -> str:
        if self.historico and self.indice_historico > 0:
            self.indice_historico -= 1
            self.entrada.delete(0, "end")
            self.entrada.insert(0, self.historico[self.indice_historico])
        return "break"

    def _historico_seguinte(self, _evento=None) -> str:
        if self.indice_historico < len(self.historico) - 1:
            self.indice_historico += 1
            self.entrada.delete(0, "end")
            self.entrada.insert(0, self.historico[self.indice_historico])
        else:
            self.indice_historico = len(self.historico)
            self.entrada.delete(0, "end")
        return "break"

    def pasta_inicial(self):
        """Comeca em `frontend/`: e onde vive o package.json."""
        return FRONTEND if FRONTEND.is_dir() else RAIZ
