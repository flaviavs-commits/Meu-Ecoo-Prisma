"""Painel que lista portas em uso na maquina e deixa encerra-las."""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont

from ..desenho import retangulo_redondo
from ..tokens import (
    BORDA,
    BORDA_HOVER,
    FUNDO,
    RAIO,
    SUPERFICIE,
    TEXTO,
    TEXTO_SUAVE,
    TEXTO_TENUE,
)
from .barra_rolagem import BarraRolagem
from .botao_modal import BotaoModal


class PainelPortas:
    """Janela com a lista de portas TCP em escuta, uma por linha.

    Cada linha mostra a porta, o processo dono e o projeto deduzido da
    linha de comando, com um botao para encerrar so aquele processo. A
    lista e recarregada a cada abertura - nao ha por que manter estado
    entre uma chamada e outra.
    """

    LARGURA = 460
    ALTURA = 420

    def __init__(
        self,
        pai: tk.Tk,
        fontes: dict[str, tkfont.Font],
        portas,
        ao_encerrar,
    ) -> None:
        self.ao_encerrar = ao_encerrar
        self.fontes = fontes

        self.janela = tk.Toplevel(pai)
        self.janela.title("Portas em uso")
        self.janela.configure(bg=FUNDO)
        self.janela.resizable(False, False)
        self.janela.transient(pai)
        self.janela.overrideredirect(True)

        self.tela = tk.Canvas(self.janela, bg=FUNDO, highlightthickness=0, bd=0)
        self.tela.pack(fill="both", expand=True)
        self.tela.bind("<Configure>", lambda _e: self._redesenhar_moldura())

        moldura = tk.Frame(self.tela, bg=SUPERFICIE)
        self.tela.create_window(0, 0, window=moldura, anchor="nw", tags="conteudo")

        tk.Label(
            moldura, text="Portas em uso", font=fontes["modal_titulo"],
            bg=SUPERFICIE, fg=TEXTO,
        ).pack(anchor="w", padx=26, pady=(24, 0))

        tk.Label(
            moldura,
            text="Processos escutando portas TCP nesta máquina.",
            font=fontes["card_desc"], bg=SUPERFICIE, fg=TEXTO_SUAVE,
        ).pack(anchor="w", padx=26, pady=(4, 14))

        area = tk.Frame(moldura, bg=SUPERFICIE, width=self.LARGURA, height=self.ALTURA)
        area.pack(padx=26)
        area.pack_propagate(False)

        self.lista = tk.Text(
            area, bg=SUPERFICIE, relief="flat", bd=0, highlightthickness=0,
            wrap="none", cursor="arrow", state="disabled",
        )
        self.lista.pack(side="left", fill="both", expand=True)
        self.rolagem = BarraRolagem(area, self.lista)
        self.rolagem.canvas.configure(bg=SUPERFICIE)
        self.rolagem.canvas.pack(side="right", fill="y")

        rodape = tk.Frame(moldura, bg=SUPERFICIE)
        rodape.pack(fill="x", padx=26, pady=(14, 22))
        BotaoModal(
            rodape, "Fechar", self._fechar, fontes["modal_botao"], primario=True,
        ).canvas.pack(side="right")

        self.janela.bind("<Escape>", lambda _e: self._fechar())

        self._preencher(portas)

        moldura.update_idletasks()
        largura = moldura.winfo_reqwidth()
        altura = moldura.winfo_reqheight()
        self.tela.itemconfig("conteudo", width=largura, height=altura)
        self.janela.geometry(f"{largura}x{altura}")
        self._centralizar(pai)

        self.janela.grab_set()
        self.janela.lift()
        self.janela.focus_force()

    def _preencher(self, portas) -> None:
        self.lista.config(state="normal")
        self.lista.delete("1.0", "end")

        if not portas:
            self.lista.insert("end", "Nenhuma porta em escuta encontrada.")
            self.lista.config(state="disabled", fg=TEXTO_TENUE)
            return

        for indice, item in enumerate(portas):
            linha = tk.Frame(self.lista, bg=SUPERFICIE)
            if indice:
                tk.Frame(linha, bg=BORDA, height=1).pack(fill="x", pady=(0, 9))

            topo = tk.Frame(linha, bg=SUPERFICIE)
            topo.pack(fill="x")

            tk.Label(
                topo, text=f":{item.porta}", font=self.fontes["card_titulo"],
                bg=SUPERFICIE, fg=TEXTO,
            ).pack(side="left")

            tk.Label(
                topo, text=f"{item.processo}  (PID {item.pid})",
                font=self.fontes["dica"], bg=SUPERFICIE, fg=TEXTO_TENUE,
            ).pack(side="left", padx=(10, 0))

            BotaoModal(
                topo, "Encerrar", self._gerar_encerrar(item), self.fontes["modal_botao"],
                largura=78,
            ).canvas.pack(side="right")

            if item.projeto:
                tk.Label(
                    linha, text=item.projeto, font=self.fontes["dica"],
                    bg=SUPERFICIE, fg=TEXTO_SUAVE, anchor="w",
                ).pack(fill="x", pady=(3, 0))

            linha.pack(fill="x", pady=(0, 9) if indice == 0 else (9, 9))
            self.lista.window_create("end", window=linha, stretch=True)
            self.lista.insert("end", "\n")

        self.lista.config(state="disabled")

    def _gerar_encerrar(self, item):
        def encerrar() -> None:
            self.ao_encerrar(item)
            self._fechar()

        return encerrar

    def _redesenhar_moldura(self) -> None:
        largura = self.tela.winfo_width()
        altura = self.tela.winfo_height()
        if largura <= 1 or altura <= 1:
            return
        self.tela.delete("moldura")
        retangulo_redondo(
            self.tela, 0, 0, largura, altura, RAIO,
            fill=SUPERFICIE, outline=BORDA_HOVER, width=1, tags="moldura",
        )
        self.tela.tag_lower("moldura")

    def _centralizar(self, pai: tk.Tk) -> None:
        self.janela.update_idletasks()
        largura = self.janela.winfo_width()
        altura = self.janela.winfo_height()
        x = pai.winfo_rootx() + (pai.winfo_width() - largura) // 2
        y = pai.winfo_rooty() + (pai.winfo_height() - altura) // 3
        self.janela.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.janela.update()

    def _fechar(self) -> None:
        self.janela.destroy()
