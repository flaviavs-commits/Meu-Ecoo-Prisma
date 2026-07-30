"""A janela do HUD: estado, fila de eventos e composicao dos mixins.

O comportamento vive nos mixins - `LayoutMixin` monta, `StatusMixin` mede,
`ConsoleMixin` executa o que se digita, `AcoesMixin` responde aos cards.
Aqui ficam so o estado compartilhado e a ponte entre thread e interface.
"""

from __future__ import annotations

import queue
import subprocess
import tkinter as tk

from .acoes import AcoesMixin
from .caminhos import PORTA_PADRAO
from .console import ConsoleMixin
from .fontes import preparar_fontes
from .layout import LayoutMixin
from .processos import limpar_ansi
from .status import StatusMixin
from .tokens import ERRO, ERRO_FUNDO, SUCESSO, SUCESSO_FUNDO
from .widgets import CardAcao


class Hud(LayoutMixin, StatusMixin, ConsoleMixin, AcoesMixin):
    """Janela de entrada: estado do ambiente e acoes."""

    def __init__(self, raiz: tk.Tk) -> None:
        self.raiz = raiz
        self.porta = PORTA_PADRAO
        self.servidor: subprocess.Popen[str] | None = None

        # As acoes rodam em thread para nao congelar a janela; a saida
        # volta por esta fila, lida pelo laco do Tkinter.
        self.fila: queue.Queue[tuple[str, str]] = queue.Queue()
        self.ocupado = False
        self.cards: dict[str, CardAcao] = {}
        self.rodando = False
        self._toast: tk.Frame | None = None
        self._toast_tarefa: str | None = None

        # Console interativo: historico de comandos e o processo em curso
        # (guardado para o Ctrl+C poder encerrar).
        self.historico: list[str] = []
        self.indice_historico = 0
        self.processo_shell: subprocess.Popen[bytes] | None = None
        self.pasta_console = self.pasta_inicial()

        self.fontes = preparar_fontes(self.raiz)
        self._montar()
        self._ajustar_altura()
        self._drenar_fila()
        self._agendar_status()
        self._surgir()

    # -- console e avisos ----------------------------------------------

    def _escrever(self, texto: str, tag: str = "") -> None:
        self.console.config(state="normal")
        self.console.insert("end", limpar_ansi(texto).rstrip() + "\n", tag)
        self.console.see("end")
        self.console.config(state="disabled")

    def _toast_mostrar(self, texto: str, sucesso: bool = True) -> None:
        """Aviso flutuante no rodape, que some sozinho."""
        if self._toast is not None:
            self._toast.destroy()
        if self._toast_tarefa is not None:
            self.raiz.after_cancel(self._toast_tarefa)

        cor = SUCESSO if sucesso else ERRO
        fundo = SUCESSO_FUNDO if sucesso else ERRO_FUNDO

        self._toast = tk.Frame(
            self.raiz, bg=fundo, highlightbackground=cor, highlightthickness=1
        )
        tk.Label(
            self._toast, text=f"{'✓' if sucesso else '✕'}  {texto}",
            font=self.fontes["toast"], bg=fundo, fg=cor, padx=18, pady=10,
        ).pack()
        self._toast.place(relx=0.5, rely=1.0, y=-26, anchor="s")

        self._toast_tarefa = self.raiz.after(3200, self._toast_esconder)

    def _toast_esconder(self) -> None:
        if self._toast is not None:
            self._toast.destroy()
            self._toast = None
        self._toast_tarefa = None

    # -- ponte thread -> interface -------------------------------------

    def _drenar_fila(self) -> None:
        """Traz para a janela o que as threads produziram."""
        try:
            while True:
                tipo, texto = self.fila.get_nowait()
                if tipo == "fim":
                    self._travar_cards(False)
                elif tipo == "status":
                    self._pintar_status(bool(texto))
                elif tipo == "toast_ok":
                    self._toast_mostrar(texto, True)
                elif tipo == "toast_erro":
                    self._toast_mostrar(texto, False)
                else:
                    self._escrever(texto, tipo)
        except queue.Empty:
            pass
        self.raiz.after(120, self._drenar_fila)
