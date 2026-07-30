"""Janela de dialogo na identidade do projeto."""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont

from ..desenho import retangulo_redondo
from ..tokens import (
    BORDA_HOVER,
    ERRO,
    FUNDO,
    RAIO,
    SUPERFICIE,
    TEXTO,
    TEXTO_SUAVE,
    TEXTO_TENUE,
)
from .botao_modal import BotaoModal


class Modal:
    """Janela de dialogo na identidade do projeto.

    Substitui `simpledialog` e `messagebox`, que desenham o widget cru do
    Windows - fundo cinza, botao com relevo, fonte do sistema. Aqui a
    janela usa a mesma paleta, tipografia e cantos dos cards.

    Modal de verdade: `transient` + `grab_set` prendem o foco, Enter
    confirma, Esc cancela.
    """

    def __init__(
        self,
        pai: tk.Tk,
        fontes: dict[str, tkfont.Font],
        titulo: str,
        mensagem: str,
        confirmar: str = "Confirmar",
        cancelar: str = "Cancelar",
        valor_inicial: str | None = None,
        dica: str = "",
    ) -> None:
        self.resultado: str | None = None
        self.fontes = fontes
        self.tem_entrada = valor_inicial is not None

        self.janela = tk.Toplevel(pai)
        self.janela.title(titulo)
        # O fundo da janela e o tom do FUNDO da landing, nao o da
        # SUPERFICIE do cartao: e o que aparece nos 4 cantos onde o
        # retangulo arredondado deixa de cobrir - o mesmo truque dos
        # cards. Sem isso, o corte do arredondado mostraria um quadrado
        # branco atras.
        self.janela.configure(bg=FUNDO)
        self.janela.resizable(False, False)
        self.janela.transient(pai)

        # Sem barra de titulo do sistema o modal fica coerente com o
        # resto; o titulo e desenhado por nos.
        self.janela.overrideredirect(True)

        # A moldura arredondada e desenhada em Canvas, como os cards:
        # `tk.Frame` com `highlightthickness` so faz cantos retos.
        self.tela = tk.Canvas(self.janela, bg=FUNDO, highlightthickness=0, bd=0)
        self.tela.pack(fill="both", expand=True)
        self.tela.bind("<Configure>", lambda _e: self._redesenhar_moldura())

        moldura = tk.Frame(self.tela, bg=SUPERFICIE)
        self.tela.create_window(0, 0, window=moldura, anchor="nw", tags="conteudo")

        tk.Label(
            moldura, text=titulo, font=fontes["modal_titulo"],
            bg=SUPERFICIE, fg=TEXTO,
        ).pack(anchor="w", padx=26, pady=(24, 0))

        tk.Label(
            moldura, text=mensagem, font=fontes["card_desc"],
            bg=SUPERFICIE, fg=TEXTO_SUAVE, justify="left", wraplength=320,
        ).pack(anchor="w", padx=26, pady=(6, 0))

        if self.tem_entrada:
            caixa = tk.Frame(
                moldura, bg=FUNDO,
                highlightbackground=BORDA_HOVER, highlightthickness=1,
            )
            caixa.pack(fill="x", padx=26, pady=(16, 0))

            self.entrada = tk.Entry(
                caixa, font=fontes["modal_entrada"], bg=FUNDO, fg=TEXTO,
                relief="flat", bd=0, highlightthickness=0,
                insertbackground=TEXTO, justify="left",
            )
            self.entrada.pack(fill="x", padx=14, pady=11)
            self.entrada.insert(0, valor_inicial or "")
            self.entrada.select_range(0, "end")

            if dica:
                tk.Label(
                    moldura, text=dica, font=fontes["dica"],
                    bg=SUPERFICIE, fg=TEXTO_TENUE,
                ).pack(anchor="w", padx=26, pady=(7, 0))

        self.aviso = tk.Label(
            moldura, text="", font=fontes["dica"], bg=SUPERFICIE, fg=ERRO,
        )
        self.aviso.pack(anchor="w", padx=26)

        linha = tk.Frame(moldura, bg=SUPERFICIE)
        linha.pack(fill="x", padx=26, pady=(14, 22))

        # Ordem invertida: `side="right"` empilha da direita para a
        # esquerda, entao o primario e adicionado primeiro para terminar
        # na ponta direita, como manda a convencao no Windows.
        BotaoModal(
            linha, confirmar, self._confirmar, fontes["modal_botao"], primario=True
        ).canvas.pack(side="right")
        tk.Frame(linha, bg=SUPERFICIE, width=8).pack(side="right")
        BotaoModal(
            linha, cancelar, self._cancelar, fontes["modal_botao"]
        ).canvas.pack(side="right")

        self.janela.bind("<Return>", lambda _e: self._confirmar())
        self.janela.bind("<Escape>", lambda _e: self._cancelar())

        # A janela e dimensionada pelo conteudo do Frame interno, ja que
        # o Canvas nao encolhe sozinho como o Frame fazia antes.
        moldura.update_idletasks()
        largura = moldura.winfo_reqwidth()
        altura = moldura.winfo_reqheight()
        self.tela.itemconfig("conteudo", width=largura, height=altura)
        self.janela.geometry(f"{largura}x{altura}")

        self._centralizar(pai)

        # `focus_set` so agenda o foco; se o SO ainda tiver o foco preso
        # em outro widget (por exemplo, o console apos um modal anterior
        # fechar), o pedido fica sem efeito e o Escape/Enter param de
        # funcionar - reproduzido ao abrir este modal duas vezes seguidas.
        # `focus_force` toma o foco na hora, e sem ele nem sempre "grab"
        # bastava.
        self.janela.grab_set()
        self.janela.lift()
        if self.tem_entrada:
            self.entrada.focus_force()
        else:
            self.janela.focus_force()

    def _redesenhar_moldura(self) -> None:
        """Desenha o fundo arredondado atras do conteudo do modal."""
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
        # Com `overrideredirect(True)` (sem decoracao), o Windows so
        # reflete a posicao real depois de um ciclo do laco principal -
        # `update_idletasks()` nao basta. Sem o `update()`, a janela
        # nasce em 0,0 (canto superior esquerdo da tela) por uma corrida
        # e so se corrige no proximo evento, visivel como um pulo.
        self.janela.update_idletasks()
        largura = self.janela.winfo_width()
        altura = self.janela.winfo_height()
        x = pai.winfo_rootx() + (pai.winfo_width() - largura) // 2
        y = pai.winfo_rooty() + (pai.winfo_height() - altura) // 3
        self.janela.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.janela.update()

    def avisar(self, texto: str) -> None:
        """Mostra um erro dentro do proprio modal, sem fechar."""
        self.aviso.config(text=texto)

    def _confirmar(self) -> None:
        self.resultado = self.entrada.get() if self.tem_entrada else "sim"
        self.janela.destroy()

    def _cancelar(self) -> None:
        self.resultado = None
        self.janela.destroy()

    def esperar(self) -> str | None:
        """Bloqueia ate o modal fechar e devolve o resultado."""
        self.janela.wait_window()
        return self.resultado
